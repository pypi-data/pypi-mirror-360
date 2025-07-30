import os
import base64
from typing import Union, Optional, cast

from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.boxes.action_ai_params import ActionAIParams
from gbox_sdk.types.v1.boxes.action_ai_response import ActionAIResponse
from gbox_sdk.types.v1.boxes.action_drag_params import DragSimple, DragAdvanced, ActionDragParams
from gbox_sdk.types.v1.boxes.action_move_params import ActionMoveParams
from gbox_sdk.types.v1.boxes.action_type_params import ActionTypeParams
from gbox_sdk.types.v1.boxes.action_click_params import ActionClickParams
from gbox_sdk.types.v1.boxes.action_swipe_params import SwipeSimple, SwipeAdvanced
from gbox_sdk.types.v1.boxes.action_touch_params import ActionTouchParams
from gbox_sdk.types.v1.boxes.action_drag_response import ActionDragResponse
from gbox_sdk.types.v1.boxes.action_move_response import ActionMoveResponse
from gbox_sdk.types.v1.boxes.action_scroll_params import ActionScrollParams
from gbox_sdk.types.v1.boxes.action_type_response import ActionTypeResponse
from gbox_sdk.types.v1.boxes.action_click_response import ActionClickResponse
from gbox_sdk.types.v1.boxes.action_swipe_response import ActionSwipeResponse
from gbox_sdk.types.v1.boxes.action_touch_response import ActionTouchResponse
from gbox_sdk.types.v1.boxes.action_scroll_response import ActionScrollResponse
from gbox_sdk.types.v1.boxes.action_press_key_params import ActionPressKeyParams
from gbox_sdk.types.v1.boxes.action_screenshot_params import ActionScreenshotParams
from gbox_sdk.types.v1.boxes.action_press_key_response import ActionPressKeyResponse
from gbox_sdk.types.v1.boxes.action_press_button_params import ActionPressButtonParams
from gbox_sdk.types.v1.boxes.action_screenshot_response import ActionScreenshotResponse
from gbox_sdk.types.v1.boxes.action_press_button_response import ActionPressButtonResponse
from gbox_sdk.types.v1.boxes.action_screen_rotation_params import ActionScreenRotationParams
from gbox_sdk.types.v1.boxes.action_screen_rotation_response import ActionScreenRotationResponse


class ActionScreenshot(ActionScreenshotParams, total=False):
    """
    Extends ActionScreenshotParams to optionally include a file path for saving the screenshot.

    Attributes:
        path (Optional[str]): The file path where the screenshot will be saved.
    """

    path: Optional[str]


class ActionAI(ActionAIParams, total=False):
    """
    Extends ActionAIParams for AI-based actions.
    """

    pass


class ActionOperator:
    """
    Provides high-level action operations for a specific box using the GboxClient.

    Methods correspond to various box actions such as click, drag, swipe, type, screenshot, etc.
    """

    def __init__(self, client: GboxClient, box_id: str):
        """
        Initialize the ActionOperator.

        Args:
            client (GboxClient): The GboxClient instance to use for API calls.
            box_id (str): The ID of the box to operate on.
        """
        self.client = client
        self.box_id = box_id

    def ai(self, body: Union[str, ActionAI]) -> ActionAIResponse:
        """
        Perform an AI-powered action on the box.

        Args:
            body: Either a string instruction or ActionAI parameters.
        Returns:
            ActionAIResponse: The response from the AI action.
        """
        if isinstance(body, str):
            return self.client.v1.boxes.actions.ai(box_id=self.box_id, instruction=body)
        else:
            return self.client.v1.boxes.actions.ai(box_id=self.box_id, **body)

    def click(self, body: ActionClickParams) -> ActionClickResponse:
        """
        Perform a click action on the box.

        Args:
            body (ActionClickParams): Parameters for the click action.
        Returns:
            ActionClickResponse: The response from the click action.
        """
        return self.client.v1.boxes.actions.click(box_id=self.box_id, **body)

    def drag_simple(self, body: DragSimple) -> ActionDragResponse:
        """
        Perform a simple drag action on the box.

        Args:
            body (DragSimple): Parameters for the simple drag action.
        Returns:
            ActionDragResponse: The response from the drag action.
        """
        return self.client.v1.boxes.actions.drag(box_id=self.box_id, **body)

    def drag_advanced(self, body: DragAdvanced) -> ActionDragResponse:
        """
        Perform an advanced drag action on the box.

        Args:
            body (DragAdvanced): Parameters for the advanced drag action.
        Returns:
            ActionDragResponse: The response from the drag action.
        """
        return self.client.v1.boxes.actions.drag(box_id=self.box_id, **body)

    def drag(self, body: ActionDragParams) -> ActionDragResponse:
        """
        Perform a drag action on the box.

        Args:
            body (ActionDragParams): Parameters for the drag action.
        Returns:
            ActionDragResponse: The response from the drag action.
        """
        if body.get("path") is None:
            return self.drag_simple(cast(DragSimple, body))
        else:
            return self.drag_advanced(cast(DragAdvanced, body))

    def swipe_simple(self, body: SwipeSimple) -> ActionSwipeResponse:
        """
        Perform a simple swipe action on the box.

        Args:
            body (SwipeSimple): Parameters for the simple swipe action.
        Returns:
            ActionSwipeResponse: The response from the swipe action.
        """
        return self.client.v1.boxes.actions.swipe(box_id=self.box_id, **body)

    def swipe_advanced(self, body: SwipeAdvanced) -> ActionSwipeResponse:
        """
        Perform an advanced swipe action on the box.

        Args:
            body (SwipeAdvanced): Parameters for the advanced swipe action.
        Returns:
            ActionSwipeResponse: The response from the swipe action.
        """
        return self.client.v1.boxes.actions.swipe(box_id=self.box_id, **body)

    def press_key(self, body: ActionPressKeyParams) -> ActionPressKeyResponse:
        """
        Simulate a key press on the box.

        Args:
            body (ActionPressKeyParams): Parameters for the key press action.
        Returns:
            ActionPressKeyResponse: The response from the key press action.
        """
        return self.client.v1.boxes.actions.press_key(box_id=self.box_id, **body)

    def press_button(self, body: ActionPressButtonParams) -> ActionPressButtonResponse:
        """
        Simulate a button press on the box.

        Args:
            body (ActionPressButtonParams): Parameters for the button press action.
        Returns:
            ActionPressButtonResponse: The response from the button press action.
        """
        return self.client.v1.boxes.actions.press_button(box_id=self.box_id, **body)

    def move(self, body: ActionMoveParams) -> ActionMoveResponse:
        """
        Move an element or pointer on the box.

        Args:
            body (ActionMoveParams): Parameters for the move action.
        Returns:
            ActionMoveResponse: The response from the move action.
        """
        return self.client.v1.boxes.actions.move(box_id=self.box_id, **body)

    def scroll(self, body: ActionScrollParams) -> ActionScrollResponse:
        """
        Perform a scroll action on the box.

        Args:
            body (ActionScrollParams): Parameters for the scroll action.
        Returns:
            ActionScrollResponse: The response from the scroll action.
        """
        return self.client.v1.boxes.actions.scroll(box_id=self.box_id, **body)

    def touch(self, body: ActionTouchParams) -> ActionTouchResponse:
        """
        Simulate a touch action on the box.

        Args:
            body (ActionTouchParams): Parameters for the touch action.
        Returns:
            ActionTouchResponse: The response from the touch action.
        """
        return self.client.v1.boxes.actions.touch(box_id=self.box_id, **body)

    def type(self, body: ActionTypeParams) -> ActionTypeResponse:
        """
        Simulate typing text on the box.

        Args:
            body (ActionTypeParams): Parameters for the type action.
        Returns:
            ActionTypeResponse: The response from the type action.
        """
        return self.client.v1.boxes.actions.type(box_id=self.box_id, **body)

    def screenshot(self, body: ActionScreenshotParams) -> ActionScreenshotResponse:
        """
        Take a screenshot of the box.

        Args:
            body (ActionScreenshotParams): Parameters for the screenshot action.
        Returns:
            ActionScreenshotResponse: The response containing the screenshot data.
        """
        if body.get("output_format") is None:
            body["output_format"] = "base64"
        return self.client.v1.boxes.actions.screenshot(box_id=self.box_id, **body)

    def screen_rotation(self, body: ActionScreenRotationParams) -> ActionScreenRotationResponse:
        """
        Rotate the screen of the box.

        Args:
            body (ActionScreenRotationParams): Parameters for the screen rotation action.
        Returns:
            ActionScreenRotationResponse: The response from the screen rotation action.
        """
        return self.client.v1.boxes.actions.screen_rotation(box_id=self.box_id, **body)

    def save_data_url_to_file(self, data_url: str, file_path: str) -> None:
        """
        Save a base64-encoded data URL to a file.

        Args:
            data_url (str): The data URL containing base64-encoded data.
            file_path (str): The file path where the decoded data will be saved.
        Raises:
            ValueError: If the data URL format is invalid.
        """
        if not data_url.startswith("data:"):
            raise ValueError("Invalid data URL format")
        parts = data_url.split(",")
        if len(parts) != 2:
            raise ValueError("Invalid data URL format")
        base64_data = parts[1]

        dir_path = os.path.dirname(file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(base64_data))
