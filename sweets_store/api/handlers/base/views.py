import typing as t

from aiohttp.web import View
from asyncpgsa import PG  # type: ignore
from pydantic import BaseModel, ValidationError

from sweets_store.utils.data_parsing import get_parsing_report


class BaseView(View):
    @property
    def pg(self) -> PG:
        return self.request.app["pg"]


PARSE_MODEL_TYPE = t.TypeVar("PARSE_MODEL_TYPE", bound=BaseModel)


class BaseCreateView(BaseView, t.Generic[PARSE_MODEL_TYPE]):

    PARSE_MODEL: t.Type[PARSE_MODEL_TYPE]  # pydantic model(for example CourierCreate)

    def parse_data(
        self, data: t.List[t.Dict[str, t.Any]], index_field_name: str
    ) -> t.Tuple[bool, t.Union[t.Dict[int, t.Any], t.List[PARSE_MODEL_TYPE]]]:
        """Returns True as first element in tuple if there were parsing errors. Second element is
        an errors report if the were errors, otherwise it's a list of parsed objects
        """

        parsed_objects: t.List[PARSE_MODEL_TYPE] = []
        parsing_errors: t.Dict[int, ValidationError] = {}

        for obj_ in data:

            try:
                parsed_objects.append(self.PARSE_MODEL(**obj_))
            except ValidationError as error:
                parsing_errors[obj_[index_field_name]] = error

        if parsing_errors:
            parsing_report = get_parsing_report(parsing_errors)
            return True, parsing_report

        return False, parsed_objects
