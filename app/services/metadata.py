from typing import TypedDict


class Metadata(TypedDict, total=False):
    content_prediction: list[dict[str, str | float]]
    camera: str
