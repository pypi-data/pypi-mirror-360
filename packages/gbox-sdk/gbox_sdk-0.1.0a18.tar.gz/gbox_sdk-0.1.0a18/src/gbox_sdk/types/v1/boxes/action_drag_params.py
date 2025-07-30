# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from ...._utils import PropertyInfo

__all__ = ["ActionDragParams", "DragSimple", "DragSimpleEnd", "DragSimpleStart", "DragAdvanced", "DragAdvancedPath"]


class DragSimple(TypedDict, total=False):
    end: Required[DragSimpleEnd]
    """Single point in a drag path"""

    start: Required[DragSimpleStart]
    """Single point in a drag path"""

    duration: str
    """Duration to complete the movement from start to end coordinates

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms
    """

    include_screenshot: Annotated[bool, PropertyInfo(alias="includeScreenshot")]
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """Type of the URI. default is base64."""

    screenshot_delay: Annotated[str, PropertyInfo(alias="screenshotDelay")]
    """Delay after performing the action, before taking the final screenshot.

    Execution flow:

    1. Take screenshot before action
    2. Perform the action
    3. Wait for screenshotDelay (this parameter)
    4. Take screenshot after action

    Example: '500ms' means wait 500ms after the action before capturing the final
    screenshot.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s
    """


class DragSimpleEnd(TypedDict, total=False):
    x: Required[float]
    """X coordinate of a point in the drag path"""

    y: Required[float]
    """Y coordinate of a point in the drag path"""


class DragSimpleStart(TypedDict, total=False):
    x: Required[float]
    """X coordinate of a point in the drag path"""

    y: Required[float]
    """Y coordinate of a point in the drag path"""


class DragAdvanced(TypedDict, total=False):
    path: Required[Iterable[DragAdvancedPath]]
    """Path of the drag action as a series of coordinates"""

    duration: str
    """Time interval between points (e.g. "50ms")

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 50ms
    """

    include_screenshot: Annotated[bool, PropertyInfo(alias="includeScreenshot")]
    """Whether to include screenshots in the action response.

    If false, the screenshot object will still be returned but with empty URIs.
    Default is false.
    """

    output_format: Annotated[Literal["base64", "storageKey"], PropertyInfo(alias="outputFormat")]
    """Type of the URI. default is base64."""

    screenshot_delay: Annotated[str, PropertyInfo(alias="screenshotDelay")]
    """Delay after performing the action, before taking the final screenshot.

    Execution flow:

    1. Take screenshot before action
    2. Perform the action
    3. Wait for screenshotDelay (this parameter)
    4. Take screenshot after action

    Example: '500ms' means wait 500ms after the action before capturing the final
    screenshot.

    Supported time units: ms (milliseconds), s (seconds), m (minutes), h (hours)
    Example formats: "500ms", "30s", "5m", "1h" Default: 500ms Maximum allowed: 30s
    """


class DragAdvancedPath(TypedDict, total=False):
    x: Required[float]
    """X coordinate of a point in the drag path"""

    y: Required[float]
    """Y coordinate of a point in the drag path"""


ActionDragParams: TypeAlias = Union[DragSimple, DragAdvanced]
