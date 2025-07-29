from functools import partial
from typing import Generic, TypeVar

from penta.dependencies.depends import _Depends
from penta.signature.parser import Signature

T = TypeVar("T")


class BaseCustom(_Depends, Generic[T]):
    annotation_type: type[T]

    def __init__(
        self,
        *,
        use_cache: bool = True,
        cast: bool = True,
    ) -> None:
        dependency = partial(self.__call__)
        dependency.__signature__ = Signature.from_callable(self.__call__)
        super().__init__(dependency, use_cache=use_cache, cast=cast)
        self.param_name: str | None = None
        self.annotation_type: type[T]
        self.default: type[T]
