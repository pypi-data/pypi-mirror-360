# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ActionScreenRotationParams"]


class ActionScreenRotationParams(TypedDict, total=False):
    angle: Required[Literal[90, 180, 270]]
    """Rotation angle in degrees"""

    direction: Required[Literal["clockwise", "counter-clockwise"]]
    """Rotation direction"""
