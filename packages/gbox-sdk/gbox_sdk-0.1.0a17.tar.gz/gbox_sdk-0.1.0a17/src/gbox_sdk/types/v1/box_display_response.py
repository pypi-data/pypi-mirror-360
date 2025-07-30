# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal

from ..._models import BaseModel

__all__ = ["BoxDisplayResponse", "Resolution"]


class Resolution(BaseModel):
    height: float
    """Height of the box"""

    width: float
    """Width of the box"""


class BoxDisplayResponse(BaseModel):
    orientation: Literal["portrait", "landscape", "landscape-reverse", "portrait-reverse"]
    """Orientation of the box"""

    resolution: Resolution
    """Box display resolution configuration"""
