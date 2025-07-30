# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gbox_sdk import GboxClient, AsyncGboxClient
from tests.utils import assert_matches_type
from gbox_sdk.types.v1.boxes import (
    ActionAIResponse,
    ActionDragResponse,
    ActionMoveResponse,
    ActionTypeResponse,
    ActionClickResponse,
    ActionSwipeResponse,
    ActionTouchResponse,
    ActionScrollResponse,
    ActionExtractResponse,
    ActionPressKeyResponse,
    ActionScreenshotResponse,
    ActionPressButtonResponse,
    ActionScreenRotationResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestActions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip()
    @parametrize
    def test_method_ai(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.ai(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="click the login button",
        )
        assert_matches_type(ActionAIResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_ai_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.ai(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="click the login button",
            background="The user is on the login page",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
            settings={
                "system_prompt": "You are a helpful assistant specialized in UI automation. When given a screenshot and instruction, analyze the visual elements carefully and execute the most appropriate action. Always prioritize user safety and avoid destructive actions unless explicitly requested."
            },
        )
        assert_matches_type(ActionAIResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_ai(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.ai(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="click the login button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionAIResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_ai(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.ai(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="click the login button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionAIResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_ai(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.ai(
                box_id="",
                instruction="click the login button",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_click(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=100,
            y=100,
        )
        assert_matches_type(ActionClickResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_click_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=100,
            y=100,
            button="left",
            double=False,
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionClickResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_click(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=100,
            y=100,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionClickResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_click(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=100,
            y=100,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionClickResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_click(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.click(
                box_id="",
                x=100,
                y=100,
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_drag_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_drag_with_all_params_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
            duration="500ms",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_drag_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_drag_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionDragResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_drag_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.drag(
                box_id="",
                end={
                    "x": 400,
                    "y": 300,
                },
                start={
                    "x": 100,
                    "y": 150,
                },
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_drag_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        )
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_drag_with_all_params_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
            duration="50ms",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_drag_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_drag_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionDragResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_drag_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.drag(
                box_id="",
                path=[
                    {
                        "x": 100,
                        "y": 150,
                    },
                    {
                        "x": 200,
                        "y": 200,
                    },
                    {
                        "x": 300,
                        "y": 250,
                    },
                ],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_extract(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        )
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_extract_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
            schema={},
        )
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_extract(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_extract(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionExtractResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_extract(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.extract(
                box_id="",
                instruction="Extract the email address from the UI interface",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_move(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        )
        assert_matches_type(ActionMoveResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_move_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionMoveResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_move(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionMoveResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_move(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionMoveResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_move(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.move(
                box_id="",
                x=200,
                y=300,
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_press_button(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        )
        assert_matches_type(ActionPressButtonResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_press_button_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionPressButtonResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_press_button(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionPressButtonResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_press_button(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionPressButtonResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_press_button(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.press_button(
                box_id="",
                buttons=["power"],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_press_key(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        )
        assert_matches_type(ActionPressKeyResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_press_key_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionPressKeyResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_press_key(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionPressKeyResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_press_key(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionPressKeyResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_press_key(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.press_key(
                box_id="",
                keys=["enter"],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_screen_rotation(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            angle=90,
            direction="clockwise",
        )
        assert_matches_type(ActionScreenRotationResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_screen_rotation(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            angle=90,
            direction="clockwise",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionScreenRotationResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_screen_rotation(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            angle=90,
            direction="clockwise",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionScreenRotationResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_screen_rotation(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.screen_rotation(
                box_id="",
                angle=90,
                direction="clockwise",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_screenshot(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_screenshot_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            clip={
                "height": 600,
                "width": 800,
                "x": 100,
                "y": 50,
            },
            output_format="base64",
        )
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_screenshot(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_screenshot(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionScreenshotResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_screenshot(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.screenshot(
                box_id="",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_scroll(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=100,
            x=100,
            y=100,
        )
        assert_matches_type(ActionScrollResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_scroll_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=100,
            x=100,
            y=100,
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionScrollResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_scroll(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=100,
            x=100,
            y=100,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionScrollResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_scroll(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=100,
            x=100,
            y=100,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionScrollResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_scroll(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.scroll(
                box_id="",
                scroll_x=0,
                scroll_y=100,
                x=100,
                y=100,
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_swipe_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_swipe_with_all_params_overload_1(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
            distance=300,
            duration="500ms",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_swipe_overload_1(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_swipe_overload_1(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionSwipeResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_swipe_overload_1(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.swipe(
                box_id="",
                direction="up",
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_swipe_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_swipe_with_all_params_overload_2(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
            duration="500ms",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_swipe_overload_2(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_swipe_overload_2(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionSwipeResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_swipe_overload_2(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.swipe(
                box_id="",
                end={
                    "x": 400,
                    "y": 300,
                },
                start={
                    "x": 100,
                    "y": 150,
                },
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_touch(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        )
        assert_matches_type(ActionTouchResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_touch_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    },
                    "actions": [
                        {
                            "type": "move",
                            "x": 400,
                            "y": 300,
                            "duration": "200ms",
                        }
                    ],
                }
            ],
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionTouchResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_touch(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionTouchResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_touch(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionTouchResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_touch(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.touch(
                box_id="",
                points=[
                    {
                        "start": {
                            "x": 100,
                            "y": 150,
                        }
                    }
                ],
            )

    @pytest.mark.skip()
    @parametrize
    def test_method_type(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        )
        assert_matches_type(ActionTypeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_method_type_with_all_params(self, client: GboxClient) -> None:
        action = client.v1.boxes.actions.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionTypeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_raw_response_type(self, client: GboxClient) -> None:
        response = client.v1.boxes.actions.with_raw_response.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = response.parse()
        assert_matches_type(ActionTypeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    def test_streaming_response_type(self, client: GboxClient) -> None:
        with client.v1.boxes.actions.with_streaming_response.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = response.parse()
            assert_matches_type(ActionTypeResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    def test_path_params_type(self, client: GboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            client.v1.boxes.actions.with_raw_response.type(
                box_id="",
                text="Hello World",
            )


class TestAsyncActions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip()
    @parametrize
    async def test_method_ai(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.ai(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="click the login button",
        )
        assert_matches_type(ActionAIResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_ai_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.ai(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="click the login button",
            background="The user is on the login page",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
            settings={
                "system_prompt": "You are a helpful assistant specialized in UI automation. When given a screenshot and instruction, analyze the visual elements carefully and execute the most appropriate action. Always prioritize user safety and avoid destructive actions unless explicitly requested."
            },
        )
        assert_matches_type(ActionAIResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_ai(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.ai(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="click the login button",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionAIResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_ai(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.ai(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="click the login button",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionAIResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_ai(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.ai(
                box_id="",
                instruction="click the login button",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_click(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=100,
            y=100,
        )
        assert_matches_type(ActionClickResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_click_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=100,
            y=100,
            button="left",
            double=False,
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionClickResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_click(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=100,
            y=100,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionClickResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_click(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.click(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=100,
            y=100,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionClickResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_click(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.click(
                box_id="",
                x=100,
                y=100,
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_drag_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_drag_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
            duration="500ms",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_drag_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_drag_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionDragResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_drag_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.drag(
                box_id="",
                end={
                    "x": 400,
                    "y": 300,
                },
                start={
                    "x": 100,
                    "y": 150,
                },
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_drag_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        )
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_drag_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
            duration="50ms",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_drag_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionDragResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_drag_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.drag(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            path=[
                {
                    "x": 100,
                    "y": 150,
                },
                {
                    "x": 200,
                    "y": 200,
                },
                {
                    "x": 300,
                    "y": 250,
                },
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionDragResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_drag_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.drag(
                box_id="",
                path=[
                    {
                        "x": 100,
                        "y": 150,
                    },
                    {
                        "x": 200,
                        "y": 200,
                    },
                    {
                        "x": 300,
                        "y": 250,
                    },
                ],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_extract(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        )
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_extract_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
            schema={},
        )
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_extract(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionExtractResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_extract(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.extract(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            instruction="Extract the email address from the UI interface",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionExtractResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_extract(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.extract(
                box_id="",
                instruction="Extract the email address from the UI interface",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_move(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        )
        assert_matches_type(ActionMoveResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_move_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionMoveResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_move(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionMoveResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_move(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.move(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            x=200,
            y=300,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionMoveResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_move(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.move(
                box_id="",
                x=200,
                y=300,
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_press_button(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        )
        assert_matches_type(ActionPressButtonResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_press_button_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionPressButtonResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_press_button(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionPressButtonResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_press_button(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.press_button(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            buttons=["power"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionPressButtonResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_press_button(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.press_button(
                box_id="",
                buttons=["power"],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_press_key(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        )
        assert_matches_type(ActionPressKeyResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_press_key_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionPressKeyResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_press_key(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionPressKeyResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_press_key(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.press_key(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            keys=["enter"],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionPressKeyResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_press_key(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.press_key(
                box_id="",
                keys=["enter"],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_screen_rotation(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            angle=90,
            direction="clockwise",
        )
        assert_matches_type(ActionScreenRotationResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_screen_rotation(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            angle=90,
            direction="clockwise",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionScreenRotationResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_screen_rotation(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.screen_rotation(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            angle=90,
            direction="clockwise",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionScreenRotationResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_screen_rotation(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.screen_rotation(
                box_id="",
                angle=90,
                direction="clockwise",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_screenshot(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_screenshot_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            clip={
                "height": 600,
                "width": 800,
                "x": 100,
                "y": 50,
            },
            output_format="base64",
        )
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_screenshot(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionScreenshotResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_screenshot(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.screenshot(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionScreenshotResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_screenshot(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.screenshot(
                box_id="",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_scroll(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=100,
            x=100,
            y=100,
        )
        assert_matches_type(ActionScrollResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_scroll_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=100,
            x=100,
            y=100,
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionScrollResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_scroll(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=100,
            x=100,
            y=100,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionScrollResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_scroll(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.scroll(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            scroll_x=0,
            scroll_y=100,
            x=100,
            y=100,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionScrollResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_scroll(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.scroll(
                box_id="",
                scroll_x=0,
                scroll_y=100,
                x=100,
                y=100,
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_swipe_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_swipe_with_all_params_overload_1(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
            distance=300,
            duration="500ms",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_swipe_overload_1(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_swipe_overload_1(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            direction="up",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionSwipeResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_swipe_overload_1(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.swipe(
                box_id="",
                direction="up",
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_swipe_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_swipe_with_all_params_overload_2(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
            duration="500ms",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_swipe_overload_2(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionSwipeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_swipe_overload_2(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.swipe(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            end={
                "x": 400,
                "y": 300,
            },
            start={
                "x": 100,
                "y": 150,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionSwipeResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_swipe_overload_2(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.swipe(
                box_id="",
                end={
                    "x": 400,
                    "y": 300,
                },
                start={
                    "x": 100,
                    "y": 150,
                },
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_touch(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        )
        assert_matches_type(ActionTouchResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_touch_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    },
                    "actions": [
                        {
                            "type": "move",
                            "x": 400,
                            "y": 300,
                            "duration": "200ms",
                        }
                    ],
                }
            ],
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionTouchResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_touch(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionTouchResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_touch(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.touch(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            points=[
                {
                    "start": {
                        "x": 100,
                        "y": 150,
                    }
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionTouchResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_touch(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.touch(
                box_id="",
                points=[
                    {
                        "start": {
                            "x": 100,
                            "y": 150,
                        }
                    }
                ],
            )

    @pytest.mark.skip()
    @parametrize
    async def test_method_type(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        )
        assert_matches_type(ActionTypeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_method_type_with_all_params(self, async_client: AsyncGboxClient) -> None:
        action = await async_client.v1.boxes.actions.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
            include_screenshot=False,
            output_format="base64",
            screenshot_delay="500ms",
        )
        assert_matches_type(ActionTypeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_raw_response_type(self, async_client: AsyncGboxClient) -> None:
        response = await async_client.v1.boxes.actions.with_raw_response.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        action = await response.parse()
        assert_matches_type(ActionTypeResponse, action, path=["response"])

    @pytest.mark.skip()
    @parametrize
    async def test_streaming_response_type(self, async_client: AsyncGboxClient) -> None:
        async with async_client.v1.boxes.actions.with_streaming_response.type(
            box_id="c9bdc193-b54b-4ddb-a035-5ac0c598d32d",
            text="Hello World",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            action = await response.parse()
            assert_matches_type(ActionTypeResponse, action, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip()
    @parametrize
    async def test_path_params_type(self, async_client: AsyncGboxClient) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `box_id` but received ''"):
            await async_client.v1.boxes.actions.with_raw_response.type(
                box_id="",
                text="Hello World",
            )
