from typing import Any, NotRequired, TypedDict


class DictResponse(TypedDict):
    predictions: NotRequired[list[Any]]
    response: NotRequired[Any]
    error: NotRequired[str]
    warning: NotRequired[str]
    step: NotRequired[Any]


def is_error(response: DictResponse | dict) -> bool:
    return response.get("error") is not None
