import typing as t

from pydantic import ValidationError


def get_parsing_errors_report(errors: t.Dict[int, ValidationError]) -> t.Dict[int, t.Any]:

    report: t.Dict[int, t.Any] = {}

    for obj_id, error in errors.items():
        report[obj_id] = {}

        for field_error in error.errors():
            field_name = field_error["loc"][0]
            error_message = field_error["msg"]

            report[obj_id][field_name] = error_message

    return report
