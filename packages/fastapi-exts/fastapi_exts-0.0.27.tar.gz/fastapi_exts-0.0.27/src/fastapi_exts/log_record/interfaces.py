import inspect
from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager, contextmanager
from functools import partial, wraps
from string import Template
from typing import (
    Annotated,
    Any,
    Generic,
    Literal,
    Self,
    TypeVar,
    cast,
    overload,
)

from fastapi.params import Depends

from fastapi_exts._utils import (
    Is,
    get_annotated_metadata,
    get_annotated_type,
    list_parameters,
    new_function,
)
from fastapi_exts.log_record._types import (
    ContextT,
    EndpointT,
    ExceptionT,
    MessageTemplate,
    P,
    T,
)
from fastapi_exts.log_record.context import (
    AnyLogRecordContextT,
    LogRecordContextT,
)
from fastapi_exts.log_record.models import (
    LogRecordFailureDetail,
    LogRecordFailureSummary,
    LogRecordSuccessDetail,
    LogRecordSuccessSummary,
)
from fastapi_exts.log_record.utils import (
    async_execute,
    is_failure,
    is_success,
    sync_execute,
)
from fastapi_exts.utils import inject_parameter, update_signature


SuccessDetailT = TypeVar("SuccessDetailT", bound=LogRecordSuccessDetail)
FailureDetailT = TypeVar("FailureDetailT", bound=LogRecordFailureDetail)


class Handler(Generic[SuccessDetailT, FailureDetailT, P]):
    def before(self, *args: P.args, **kwds: P.kwargs): ...
    def after(
        self,
        detail: SuccessDetailT | FailureDetailT,
        *args: P.args,
        **kwds: P.kwargs,
    ): ...

    def success(
        self,
        detail: SuccessDetailT,
        *args: P.args,
        **kwds: P.kwargs,
    ): ...
    def failure(
        self,
        detail: FailureDetailT,
        *args: P.args,
        **kwds: P.kwargs,
    ): ...


class AsyncHandler(Generic[SuccessDetailT, FailureDetailT, P]):
    async def before(self, *args: P.args, **kwds: P.kwargs): ...
    async def after(
        self,
        detail: SuccessDetailT | FailureDetailT,
        *args: P.args,
        **kwds: P.kwargs,
    ): ...

    async def success(
        self,
        detail: SuccessDetailT,
        *args: P.args,
        **kwds: P.kwargs,
    ): ...
    async def failure(
        self,
        detail: FailureDetailT,
        *args: Any,
        **kwds: Any,
    ): ...


_HandlerT = TypeVar("_HandlerT", bound=Handler | AsyncHandler)

_SuccessHandlerT = TypeVar("_SuccessHandlerT", bound=Callable)
_FailureHandlerT = TypeVar("_FailureHandlerT", bound=Callable)
_UtilFunctionT = TypeVar("_UtilFunctionT", bound=Callable)

_LifecycleEvent = Literal["before", "after"]


class _AbstractLogRecord(
    ABC,
    Generic[
        _HandlerT,
        _SuccessHandlerT,
        _FailureHandlerT,
        AnyLogRecordContextT,
        EndpointT,
        _UtilFunctionT,
    ],
):
    _log_record_deps_name = "__log_record_dependencies"

    def __init__(
        self,
        *,
        success: MessageTemplate | None = None,
        failure: MessageTemplate | None = None,
        functions: list[_UtilFunctionT]
        | dict[str, _UtilFunctionT]
        | None = None,
        dependencies: list[Depends] | dict[str, Depends] | None = None,
        context: AnyLogRecordContextT | None = None,
        handlers: list[_HandlerT] | None = None,
        success_handlers: list[_SuccessHandlerT] | None = None,
        failure_handlers: list[_FailureHandlerT] | None = None,
        **extra,
    ) -> None:
        self.success = success or ""
        self.failure = failure or ""

        self.dependencies: dict[str, Depends] = {}

        self.context = context

        self.functions: dict[str, _UtilFunctionT] = {}

        self.handlers = handlers or []
        self.success_handlers = success_handlers or []
        self.failure_handlers = failure_handlers or []

        # 用于判断当前装饰的是哪个端点
        self._endpoints: set[EndpointT] = set()

        if dependencies:
            if isinstance(dependencies, dict):
                for name, dep in dependencies.items():
                    self.add_dependency(dep, name)
            else:
                for dep in dependencies:
                    self.add_dependency(dep)

        if functions:
            if isinstance(functions, dict):
                for name, fn in functions.items():
                    self.register_function(fn, name)
            else:
                for fn in functions:
                    self.register_function(fn)
        self.extra = extra

    @overload
    def register_function(self, fn: _UtilFunctionT): ...
    @overload
    def register_function(self, fn: _UtilFunctionT, name: str): ...
    def register_function(self, fn: _UtilFunctionT, name: str | None = None):
        self.functions[name or fn.__name__] = fn

    def description(self) -> str | None: ...

    @overload
    def add_dependency(self, dependency: Depends): ...
    @overload
    def add_dependency(self, dependency: Depends, name: str): ...
    def add_dependency(self, dependency: Depends, name: str | None = None):
        assert callable(dependency.dependency), (
            "The dependency must be a callable function"
        )
        name = name or (
            dependency.dependency and dependency.dependency.__name__
        )

        if name in self.dependencies:
            msg = f"The dependency name {name} is already in use"
            raise ValueError(msg)

        self.dependencies.setdefault(name, dependency)

    def add_handler(self, handler: _HandlerT, /):
        self.handlers.append(handler)

    def add_success_handler(self, handler: _SuccessHandlerT, /):
        self.success_handlers.append(handler)

    def add_failure_handler(self, handler: _FailureHandlerT, /):
        self.failure_handlers.append(handler)

    @abstractmethod
    def _log_function(
        self,
        fn: Callable,
        endpoint: EndpointT,
        event: _LifecycleEvent | None,
    ) -> Callable: ...

    def _log_record_deps(self, endpoint: EndpointT):
        """创建日志所需依赖

        :param endpoint: 当日志所需依赖报错时, 导致依赖报错的端点
        :return: 日志所需依赖
        """

        if not self.dependencies:
            return None

        def log_record_dependencies(**kwargs):
            return kwargs

        parameters = []
        for name, dep in self.dependencies.items():
            assert dep.dependency is not None

            parameters.append(
                inspect.Parameter(
                    name=name,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    default=Depends(
                        self._log_function(dep.dependency, endpoint, None),
                        use_cache=dep.use_cache,
                    ),
                )
            )

        update_signature(log_record_dependencies, parameters=parameters)

        return log_record_dependencies

    def _with_log_record_deps(self, call: Callable, endpoint: EndpointT):
        # 日志记录器本身所需的依赖
        log_record_deps = self._log_record_deps(endpoint)

        if callable(log_record_deps):
            new_fn = new_function(call)
            inject_parameter(
                new_fn,
                name=self._log_record_deps_name,
                default=Depends(log_record_deps, use_cache=True),
            )

            return new_fn
        return call

    def _new_parameters(self, endpoint: EndpointT) -> list[inspect.Parameter]:
        event = "before"
        parameters: list[inspect.Parameter] = []
        for parameter in list_parameters(endpoint):
            new_parameter = parameter
            default = parameter.default
            annotation = parameter.annotation
            with_log_record_deps_dep = partial(
                self._with_log_record_deps, endpoint=endpoint
            )
            # e.g.
            # 1. def endpoint(value=Depends(dependency_function)): ...
            # 2. >>>>>>
            #    class Value:
            #        def __init__(self, demo: int):
            #            self.demo = demo
            #
            #    def endpoint(value: Value = Depends()): ...
            #    <<<<<<
            if isinstance(default, Depends):
                # handle 1
                if default.dependency:
                    new_depend = with_log_record_deps_dep(default.dependency)
                    new_dep = Depends(
                        self._log_function(new_depend, endpoint, event),
                        use_cache=default.use_cache,
                    )
                    event = None
                    new_parameter = parameter.replace(default=new_dep)
                # handle 2
                elif inspect.isclass(annotation):
                    cls = with_log_record_deps_dep(annotation)
                    new_parameter = parameter.replace(
                        annotation=self._log_function(cls, endpoint, event)
                    )
                    event = None

            # e.g.
            # 1. >>>>>>
            #    class Value:
            #        def __init__(self, demo: int):
            #            self.demo = demo
            #
            #    def endpoint(value: Annotated[Value, Depends()]): ...
            #    <<<<<<
            #
            # 2. >>>>>>
            #    def endpoint(value: Annotated[Value, Depends(dependency_function)]): ...  # noqa: E501, W505
            #    <<<<<<
            elif Is.annotated(annotation):
                typ = get_annotated_type(annotation)
                metadata = []
                cls_dep = True
                for i in get_annotated_metadata(annotation):
                    if isinstance(i, Depends):
                        if i.dependency:
                            new_depend = with_log_record_deps_dep(i.dependency)

                            cls_dep = False
                            new_dep = Depends(
                                self._log_function(
                                    new_depend, endpoint, event
                                ),
                                use_cache=default.use_cache,
                            )
                            event = None
                            metadata.append(new_dep)
                        else:
                            metadata.append(i)
                    else:
                        metadata.append(i)

                if cls_dep and inspect.isclass(typ):
                    typ = self._log_function(
                        with_log_record_deps_dep(typ),
                        endpoint,
                        event,
                    )
                    event = None

                new_parameter = parameter.replace(
                    annotation=Annotated[typ, *metadata]
                )

            parameters.append(new_parameter)
        return parameters

    @classmethod
    def new(  # noqa: PLR0913
        cls,
        *,
        old: Self,  # noqa: ARG003
        success: MessageTemplate | None = None,
        failure: MessageTemplate | None = None,
        functions: list[_UtilFunctionT]
        | dict[str, _UtilFunctionT]
        | None = None,
        dependencies: list[Depends] | dict[str, Depends] | None = None,
        context_factory: Callable[[], AnyLogRecordContextT] | None = None,
        handlers: list[_HandlerT] | None = None,
        success_handlers: list[_SuccessHandlerT] | None = None,
        failure_handlers: list[_FailureHandlerT] | None = None,
        **extra,
    ) -> Self:
        return cls(
            success=success,
            failure=failure,
            functions=functions,
            dependencies=dependencies,
            context_factory=context_factory,
            handlers=handlers,
            success_handlers=success_handlers,
            failure_handlers=failure_handlers,
            **extra,
        )

    def _new_endpoint(self, endpoint: EndpointT) -> EndpointT:
        # 日志记录器本身所需的依赖
        new_endpoint = new_function(
            endpoint,
            parameters=self._new_parameters(endpoint),
        )

        # 日志记录器本身所需的依赖
        new_endpoint = cast(
            EndpointT,
            self._with_log_record_deps(new_endpoint, endpoint),
        )

        return cast(
            EndpointT,
            self._log_function(new_endpoint, endpoint, "after"),
        )

    @overload
    def __call__(self, endpoint: EndpointT) -> EndpointT: ...

    @overload
    def __call__(
        self,
        *,
        success: MessageTemplate | None = None,
        failure: MessageTemplate | None = None,
        functions: list[_UtilFunctionT]
        | dict[str, _UtilFunctionT]
        | None = None,
        dependencies: list[Depends] | dict[str, Depends] | None = None,
        context_factory: Callable[[], AnyLogRecordContextT] | None = None,
        handlers: list[_HandlerT] | None = None,
        success_handlers: list[_SuccessHandlerT] | None = None,
        failure_handlers: list[_FailureHandlerT] | None = None,
        **extra,
    ) -> Self: ...

    def __call__(  # noqa: PLR0913
        self,
        endpoint: EndpointT | None = None,
        *,
        success: MessageTemplate | None = None,
        failure: MessageTemplate | None = None,
        functions: list[_UtilFunctionT]
        | dict[str, _UtilFunctionT]
        | None = None,
        dependencies: list[Depends] | dict[str, Depends] | None = None,
        context_factory: Callable[[], AnyLogRecordContextT] | None = None,
        handlers: list[_HandlerT] | None = None,
        success_handlers: list[_SuccessHandlerT] | None = None,
        failure_handlers: list[_FailureHandlerT] | None = None,
        **extra,
    ) -> Self | EndpointT:
        if endpoint is None:
            return self.new(
                old=self,
                success=success,
                failure=failure,
                functions=functions,
                dependencies=dependencies,
                context_factory=context_factory,
                handlers=handlers,
                success_handlers=success_handlers,
                failure_handlers=failure_handlers,
                **extra,
            )

        self._endpoints.add(endpoint)

        return self._new_endpoint(endpoint)

    @abstractmethod
    def _execute_before_handles(self, args: tuple, kwds: dict, /):
        raise NotImplementedError


class AbstractLogRecord(
    _AbstractLogRecord[
        Handler[SuccessDetailT, FailureDetailT, P],
        Callable[[SuccessDetailT], None],
        Callable[[FailureDetailT], None],
        LogRecordContextT,
        EndpointT,
        Callable[P, Any],
    ],
    ABC,
    Generic[
        SuccessDetailT,
        FailureDetailT,
        P,
        T,
        ExceptionT,
        LogRecordContextT,
        ContextT,
        EndpointT,
    ],
):
    @overload
    def format_message(
        self,
        summary: LogRecordSuccessSummary[T],
        extra: dict[str, Any] | None = None,
        context: ContextT | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str: ...
    @overload
    def format_message(
        self,
        summary: LogRecordFailureSummary[ExceptionT],
        extra: dict[str, Any] | None = None,
        context: ContextT | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str: ...
    def format_message(
        self,
        summary: LogRecordSuccessSummary[T]
        | LogRecordFailureSummary[ExceptionT],
        extra: dict[str, Any] | None = None,
        context: ContextT | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str:
        kwargs["$"] = {
            "summary": summary,
            "context": context,
            "extra": extra,
        }

        message = self.success if summary.success else self.failure

        result_ = ""

        if isinstance(message, str):
            result_ += message.format(*args, **kwargs)

        elif isinstance(message, Template):
            identifiers = message.get_identifiers()
            values = {}
            for i in identifiers:
                fn = self.functions.get(i)
                if fn:
                    values[i] = fn(*args, **kwargs)

            result_ += message.safe_substitute(
                **values,
                **kwargs,
            ).format(*args, **kwargs)

        return result_

    @abstractmethod
    def get_success_detail(
        self,
        *,
        summary: LogRecordSuccessSummary[T],
        message: str,
        context: ContextT | None,
        endpoint: EndpointT,
        extra: dict[str, Any] | None,
    ) -> SuccessDetailT:
        raise NotImplementedError

    @abstractmethod
    def get_failure_detail(
        self,
        *,
        summary: LogRecordFailureSummary,
        message: str,
        context: ContextT | None,
        endpoint: EndpointT,
        extra: dict[str, Any] | None,
    ) -> FailureDetailT:
        raise NotImplementedError

    def _execute_before_handles(self, args: tuple, kwds: dict, /):
        for i in self.handlers:
            i.before(*args, **kwds)

    def __start_context(self):
        if self.context is not None:
            self.context.start()

    def __end_context(self):
        if self.context is not None:
            self.context.end()

    @contextmanager
    def __end_ctx(self, event: _LifecycleEvent | None):
        if event == "after":
            ended = False
            try:
                yield
                ended = True
                self.__end_context()
            except:
                if ended is False:
                    ended = True
                    self.__end_context()
                raise
        else:
            try:
                yield
            except:
                self.__end_context()
                raise

    def _log_function(
        self,
        fn: Callable,
        endpoint: EndpointT,
        event: _LifecycleEvent | None,
    ):
        is_endpoint_fn = fn in self._endpoints

        @wraps(fn)
        def decorator(*args, **kwds):
            log_record_deps = kwds.pop(self._log_record_deps_name, None)
            context: ContextT | None = None
            if event == "before":
                self.__start_context()
                self._execute_before_handles(args, kwds)

            summary = sync_execute(fn, *args, **kwds)

            with self.__end_ctx(event):
                if is_endpoint_fn and is_success(summary):
                    message = self.format_message(
                        summary,
                        log_record_deps,
                        context,
                        *args,
                        **kwds,
                    )
                    detail = self.get_success_detail(
                        summary=summary,
                        context=context,
                        message=message,
                        endpoint=endpoint,
                        extra=log_record_deps,
                    )

                    for i in self.success_handlers:
                        i(detail)

                    for i in self.handlers:
                        i.success(detail, *args, **kwds)
                        i.after(detail, *args, **kwds)

                    return summary.result

                if is_failure(summary):
                    # 失败时, 依赖的上下文有可能是空的(例如如果是依赖项异常, 那么上下文是空的)  # noqa: E501, W505
                    # 如果是端点本身的异常, 则可能有值(具体看端点有没有触发上下文操作) # noqa: E501, W505
                    message = self.format_message(
                        summary,
                        log_record_deps,
                        context,
                        *args,
                        **kwds,
                    )
                    detail = self.get_failure_detail(
                        summary=summary,
                        context=context,
                        message=message,
                        endpoint=endpoint,
                        extra=log_record_deps,
                    )

                    for i in self.failure_handlers:
                        i(detail)

                    for i in self.handlers:
                        i.failure(detail, *args, **kwds)
                        i.after(detail, *args, **kwds)

                    raise summary.exception

            return summary.result

        return decorator


async def _a(v):
    if Is.awaitable(v):
        return await v
    return v


class AbstractAsyncLogRecord(
    _AbstractLogRecord[
        Handler[SuccessDetailT, FailureDetailT, P]
        | AsyncHandler[SuccessDetailT, FailureDetailT, P],
        Callable[[SuccessDetailT], None | Awaitable[None]],
        Callable[[FailureDetailT], None | Awaitable[None]],
        AnyLogRecordContextT,
        EndpointT,
        Callable[P, Awaitable | Any],
    ],
    ABC,
    Generic[
        SuccessDetailT,
        FailureDetailT,
        P,
        T,
        ExceptionT,
        AnyLogRecordContextT,
        ContextT,
        EndpointT,
    ],
):
    @overload
    async def format_message(
        self,
        summary: LogRecordSuccessSummary[T],
        extra: dict[str, Any] | None = None,
        context: ContextT | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str: ...
    @overload
    async def format_message(
        self,
        summary: LogRecordFailureSummary[ExceptionT],
        extra: dict[str, Any] | None = None,
        context: ContextT | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str: ...
    async def format_message(
        self,
        summary: LogRecordSuccessSummary[T]
        | LogRecordFailureSummary[ExceptionT],
        extra: dict[str, Any] | None = None,
        context: ContextT | None = None,
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> str:
        kwargs["$"] = {
            "summary": summary,
            "context": context,
            "extra": extra,
        }

        message = self.success if summary.success else self.failure

        result_ = ""

        if isinstance(message, str):
            result_ += message.format(*args, **kwargs)

        elif isinstance(message, Template):
            identifiers = message.get_identifiers()
            values = {}
            for i in identifiers:
                fn = self.functions.get(i)
                if fn:
                    values[i] = await _a(fn(*args, **kwargs))

            result_ += message.safe_substitute(
                **values,
                **kwargs,
            ).format(*args, **kwargs)

        return result_

    @abstractmethod
    async def get_success_detail(
        self,
        *,
        summary: LogRecordSuccessSummary[T],
        message: str,
        context: ContextT | None,
        endpoint: EndpointT,
        extra: dict[str, Any] | None,
    ) -> SuccessDetailT:
        raise NotImplementedError

    @abstractmethod
    async def get_failure_detail(
        self,
        *,
        summary: LogRecordFailureSummary,
        message: str,
        context: ContextT | None,
        endpoint: EndpointT,
        extra: dict[str, Any] | None,
    ) -> FailureDetailT:
        raise NotImplementedError

    async def _execute_before_handles(self, args: tuple, kwds: dict, /):
        for i in self.handlers:
            await _a(i.before(*args, **kwds))

    async def _execute_success_handlers(self, detail):
        for i in self.success_handlers:
            await _a(i(detail))

    async def _execute_failure_handlers(self, detail):
        for i in self.failure_handlers:
            await _a(i(detail))

    async def _execute_after_handlers(
        self,
        detail,
        args: tuple,
        kwds: dict,
        success: bool,  # noqa: FBT001
    ):
        for i in self.handlers:
            if success:
                await _a(i.success(detail, *args, **kwds))
            else:
                await _a(i.failure(detail, *args, **kwds))

            await _a(i.after(detail, *args, **kwds))

    async def __start_context(self):
        if self.context is not None:
            await _a(self.context.start())

    async def __end_context(self):
        if self.context is not None:
            await _a(self.context.end())

    @asynccontextmanager
    async def __end_ctx(self, event: _LifecycleEvent | None):
        if event == "after":
            ended = False
            try:
                yield
                ended = True
                await _a(self.__end_context())
            except:
                if ended is False:
                    ended = True
                    await _a(self.__end_context())
                raise
        else:
            try:
                yield
            except:
                await _a(self.__end_context())
                raise

    def _log_function(
        self, fn: Callable, endpoint: EndpointT, event: _LifecycleEvent | None
    ):
        is_endpoint_fn = fn in self._endpoints

        @wraps(fn)
        async def decorator(*args, **kwds):
            log_record_deps: dict[str, Any] | None = kwds.pop(
                self._log_record_deps_name, None
            )
            context: ContextT | None = None

            if event == "before":
                await self.__start_context()
                await self._execute_before_handles(args, kwds)

            summary = await async_execute(fn, *args, **kwds)
            async with self.__end_ctx(event):
                if is_endpoint_fn and is_success(summary):
                    message = await self.format_message(
                        summary,
                        log_record_deps,
                        context,
                        *args,
                        **kwds,
                    )
                    detail = await self.get_success_detail(
                        summary=summary,
                        context=context,
                        message=message,
                        endpoint=endpoint,
                        extra=log_record_deps,
                    )

                    await self._execute_success_handlers(detail)
                    await self._execute_after_handlers(
                        detail,
                        args,
                        kwds,
                        True,  # noqa: FBT003
                    )

                    return summary.result

                if is_failure(summary):
                    # 失败时, 依赖的上下文有可能是空的(例如如果是依赖项异常, 那么上下文是空的) # noqa: E501, W505
                    # 如果是端点本身的异常, 则可能有值(具体看端点有没有触发上下文操作) # noqa: E501, W505
                    message = await self.format_message(
                        summary,
                        log_record_deps,
                        context,
                        *args,
                        **kwds,
                    )
                    detail = await self.get_failure_detail(
                        summary=summary,
                        context=context,
                        message=message,
                        endpoint=endpoint,
                        extra=log_record_deps,
                    )

                    await self._execute_failure_handlers(detail)
                    await self._execute_after_handlers(
                        detail,
                        args,
                        kwds,
                        False,  # noqa: FBT003
                    )

                    raise summary.exception

                return summary.result

        return decorator
