import inspect
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Generic, Literal, TypeVar, cast

from fastapi import status
from fastapi.responses import JSONResponse, ORJSONResponse, Response
from fastapi.utils import is_body_allowed_for_status_code
from pydantic import BaseModel, create_model


try:
    import orjson  # type: ignore
except ImportError:  # pragma: nocover
    orjson = None  # type: ignore


class BaseHTTPError(Exception, ABC):
    status: int
    data: BaseModel
    headers: dict[str, str] | None

    @classmethod
    @abstractmethod
    def response_class(cls) -> type[BaseModel]:
        raise NotImplementedError


BaseModelT = TypeVar("BaseModelT", bound=BaseModel)


class WrapperError(BaseModel, Generic[BaseModelT]):
    @classmethod
    def create(
        cls: type["WrapperError[BaseModelT]"],
        model: BaseModelT,
    ) -> "WrapperError[BaseModelT]":
        raise NotImplementedError


WrapperErrorT = TypeVar("WrapperErrorT", bound=WrapperError)


class NamedHTTPError(BaseHTTPError, Generic[WrapperErrorT, BaseModelT]):
    status: int = status.HTTP_400_BAD_REQUEST
    code: str | None = None
    targets: Sequence[Any] | None = None
    target_transform: Callable[[Any], Any] | None = None
    message: str | None = None

    __wrapper__: (
        type[WrapperError[BaseModelT]]
        | tuple[WrapperErrorT, Callable[[BaseModelT], WrapperErrorT]]
        | None
    ) = None
    __create_model_name__: str | None = None

    __create_model_kwargs__: Mapping | None = None
    """
    see:
    - https://docs.pydantic.dev/latest/api/base_model/#pydantic.create_model
    - https://docs.pydantic.dev/latest/concepts/models/#dynamic-model-creation
    """

    @classmethod
    def error_name(cls):
        return cls.__name__.removesuffix("Error")

    @classmethod
    def model_class(cls) -> type[BaseModelT]:
        type_ = cls.error_name()
        error_code = cls.code or type_
        kwargs = {
            "code": (Literal[error_code], ...),
            "message": (str, ...),
        }
        if cls.targets:
            kwargs["target"] = (Literal[*cls.transformed_targets()], ...)

        kwargs.update(cls.__create_model_kwargs__ or {})

        return cast(
            type[BaseModelT],
            create_model(
                cls.__create_model_name__ or f"{type_}Model", **kwargs
            ),
        )

    @classmethod
    def error_code(cls):
        return cls.code or cls.error_name()

    @classmethod
    def transformed_targets(cls) -> list[str]:
        if cls.targets:
            result = []
            for i in cls.targets:
                if cls.target_transform:
                    result.append(cls.target_transform(i))
                else:
                    result.append(i)
            return result
        return []

    def __init__(
        self,
        *,
        message: str | None = None,
        target: str | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        kwargs: dict[str, Any] = {
            "code": self.error_code(),
            "message": message or self.message or "operation failed",
        }

        if target:
            if self.target_transform:
                target = self.target_transform(target)
            kwargs["target"] = target
            kwargs["message"] = kwargs["message"].format(target=target)

        self.model = self.model_class()(**kwargs)
        create: Callable[[BaseModelT], BaseModel] | None = None
        if inspect.isclass(self.__wrapper__):
            create = self.__wrapper__.create
        elif isinstance(self.__wrapper__, tuple):
            create = self.__wrapper__[1]

        self.data: BaseModel = (
            create(self.model) if create is not None else self.model
        )

        self.headers = headers

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.status}>"

    def __repr__(self) -> str:
        return f"<{self.model_class: str(self.error)}>"

    @classmethod
    def response_class(cls):
        model = cls.model_class()

        if cls.__wrapper__:
            wrapper: Any
            if inspect.isclass(cls.__wrapper__):
                wrapper = cls.__wrapper__
            else:
                wrapper = cls.__wrapper__[0]
            return wrapper[model]

        return model

    @classmethod
    def response_schema(cls):
        return {cls.status: {"model": cls.response_class()}}


def ext_http_error_handler(_, exc: BaseHTTPError):
    headers = getattr(exc, "headers", None)

    if not is_body_allowed_for_status_code(exc.status):
        return Response(status_code=exc.status, headers=headers)

    if orjson:
        return ORJSONResponse(
            exc.data.model_dump(exclude_none=True),
            status_code=exc.status,
            headers=headers,
        )

    return JSONResponse(
        exc.data.model_dump(exclude_none=True),
        status_code=exc.status,
        headers=headers,
    )


class EndpointError(WrapperError[BaseModelT], Generic[BaseModelT]):
    error: BaseModelT

    @classmethod
    def create(cls, model: BaseModelT):
        return cls(error=model)
