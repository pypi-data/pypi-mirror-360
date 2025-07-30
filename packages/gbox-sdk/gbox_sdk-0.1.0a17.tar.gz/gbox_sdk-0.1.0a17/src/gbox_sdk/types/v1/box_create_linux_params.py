# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ..._utils import PropertyInfo
from .create_box_config_param import CreateBoxConfigParam

__all__ = ["BoxCreateLinuxParams"]


class BoxCreateLinuxParams(TypedDict, total=False):
    config: CreateBoxConfigParam
    """Configuration for a box instance"""

    expires_in: Annotated[str, PropertyInfo(alias="expiresIn")]
    """The box will be alive for the given duration

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 60m
    """

    wait: bool
    """Wait for the box operation to be completed, default is true"""
