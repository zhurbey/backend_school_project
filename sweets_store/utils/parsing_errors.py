import typing as t

from pydantic import BaseModel, ValidationError


def get_parsing_report(errors: t.Dict[int, ValidationError]) -> t.Dict[int, t.Any]:

    report_obj: t.Dict[int, t.Any] = {}

    for obj_id, error in errors.items():
        report_obj[obj_id] = {}

        for field_error in error.errors():
            field_name = field_error["loc"][0]
            error_message = field_error["msg"]

            report_obj[obj_id][field_name] = error_message

    return report_obj
