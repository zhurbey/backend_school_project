import typing as t

from pydantic import ValidationError


def get_validation_report(error: ValidationError) -> t.Dict[str, t.Any]:
    pass
