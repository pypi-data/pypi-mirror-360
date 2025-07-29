from typing import Generic, TypeVar, cast, get_origin

from pydantic import BaseModel

from penta.dependencies.custom import BaseCustom
from penta.errors import ValidationError
from penta.request import Request

T = TypeVar("T")


class QueryParams(BaseCustom, Generic[T]):
    ITERABLES = (list, tuple, set)

    def __init__(self, param_name: str | None = None, required: bool = True):
        super().__init__()
        self.param_name = param_name
        self.required = required
        self.annotation_type: type[T]
        self.default: type[T]

    def __call__(self, request: Request) -> T | None:
        query_params = request.query_params()

        if issubclass(self.annotation_type, BaseModel):
            model_input = self._get_model_values(query_params)
            return cast(T, self.annotation_type.model_validate(model_input))

        if self.param_name and self.param_name in query_params:
            if issubclass(self.annotation_type, list):
                return self.annotation_type(query_params.getlist(self.param_name))  # type: ignore
            else:
                return self.annotation_type(query_params[self.param_name])  # type: ignore

        if self.default is not None:
            return self.default

        if self.required:
            raise ValidationError(
                [{"msg": f"Missing query parameter: {self.param_name}"}]
            )

        return None

    def _get_model_values(
        self, query_params: dict[str, str]
    ) -> dict[str, str | list[str]]:
        model_values = {}

        for field_name, field in self.annotation_type.model_fields.items():
            if field_name not in query_params:
                continue

            origin = get_origin(field.annotation)

            if origin in self.ITERABLES:
                model_values[field_name] = query_params.getlist(field_name)
                continue

            try:
                if issubclass(origin, self.ITERABLES):
                    model_values[field_name] = query_params.getlist(field_name)
                else:
                    model_values[field_name] = query_params.get(field_name)
            except TypeError:
                model_values[field_name] = query_params.get(field_name)
            finally:
                continue

        return model_values
