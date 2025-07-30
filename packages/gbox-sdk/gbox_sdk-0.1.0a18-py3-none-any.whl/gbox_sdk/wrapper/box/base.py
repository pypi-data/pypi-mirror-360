from typing import List, Union, Optional

from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.linux_box import LinuxBox
from gbox_sdk.wrapper.box.action import ActionOperator
from gbox_sdk.wrapper.box.browser import BrowserOperator
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.wrapper.box.file_system import FileSystemOperator
from gbox_sdk.types.v1.box_stop_params import BoxStopParams
from gbox_sdk.types.v1.box_start_params import BoxStartParams
from gbox_sdk.types.v1.box_run_code_params import BoxRunCodeParams
from gbox_sdk.types.v1.box_terminate_params import BoxTerminateParams
from gbox_sdk.types.v1.box_run_code_response import BoxRunCodeResponse
from gbox_sdk.types.v1.box_live_view_url_params import BoxLiveViewURLParams
from gbox_sdk.types.v1.box_live_view_url_response import BoxLiveViewURLResponse
from gbox_sdk.types.v1.box_execute_commands_params import BoxExecuteCommandsParams
from gbox_sdk.types.v1.box_web_terminal_url_params import BoxWebTerminalURLParams
from gbox_sdk.types.v1.box_execute_commands_response import BoxExecuteCommandsResponse
from gbox_sdk.types.v1.box_web_terminal_url_response import BoxWebTerminalURLResponse


class BaseBox:
    """
    Base class for box operations, providing common interfaces for box lifecycle and actions.

    Attributes:
        client (GboxClient): The Gbox client instance used for API calls.
        data (Union[LinuxBox, AndroidBox]): The box data object.
        action (ActionOperator): Operator for box actions.
        fs (FileSystemOperator): Operator for file system actions.
        browser (BrowserOperator): Operator for browser actions.
    """

    def __init__(self, client: GboxClient, data: Union[LinuxBox, AndroidBox]):
        """
        Initialize a BaseBox instance.

        Args:
            client (GboxClient): The Gbox client instance.
            data (Union[LinuxBox, AndroidBox]): The box data object.
        """
        self.client = client
        self.data = data

        self.action = ActionOperator(self.client, self.data.id)
        self.fs = FileSystemOperator(self.client, self.data.id)
        self.browser = BrowserOperator(self.client, self.data.id)

    def _sync_data(self) -> None:
        """
        Synchronize the box data with the latest state from the server.
        """
        res = self.client.v1.boxes.retrieve(box_id=self.data.id)
        self.data = res

    def start(self, body: BoxStartParams) -> "BaseBox":
        """
        Start the box.

        Args:
            body (BoxStartParams): Parameters for starting the box.
        Returns:
            BaseBox: The updated box instance.
        """
        self.client.v1.boxes.start(box_id=self.data.id, **body)
        self._sync_data()
        return self

    def stop(self, body: BoxStopParams) -> "BaseBox":
        """
        Stop the box.

        Args:
            body (BoxStopParams): Parameters for stopping the box.
        Returns:
            BaseBox: The updated box instance.
        """
        self.client.v1.boxes.stop(box_id=self.data.id, **body)
        self._sync_data()
        return self

    def terminate(self, body: BoxTerminateParams) -> "BaseBox":
        """
        Terminate the box.

        Args:
            body (BoxTerminateParams): Parameters for terminating the box.
        Returns:
            BaseBox: The updated box instance.
        """
        self.client.v1.boxes.terminate(box_id=self.data.id, **body)
        self._sync_data()
        return self

    def command(self, body: Union[BoxExecuteCommandsParams, str, List[str]]) -> "BoxExecuteCommandsResponse":
        """
        Execute shell commands in the box.

        Args:
            body (Union[BoxExecuteCommandsParams, str, List[str]]): The commands to execute or parameters object.
        Returns:
            BoxExecuteCommandsResponse: The response containing the command execution result.
        """
        if isinstance(body, str):
            body = BoxExecuteCommandsParams(commands=[body])
        elif isinstance(body, list):
            body = BoxExecuteCommandsParams(commands=body)
        return self.client.v1.boxes.execute_commands(box_id=self.data.id, **body)

    def run_code(self, body: Union[BoxRunCodeParams, str]) -> "BoxRunCodeResponse":
        """
        Run code in the box.

        Args:
            body (Union[BoxRunCodeParams, str]): The code to run or parameters object.
        Returns:
            BoxRunCodeResponse: The response containing the code execution result.
        """
        if isinstance(body, str):
            body = BoxRunCodeParams(code=body)
        return self.client.v1.boxes.run_code(box_id=self.data.id, **body)

    def live_view(self, body: Optional[BoxLiveViewURLParams] = None) -> BoxLiveViewURLResponse:
        """
        Get the live view URL for the box.

        Args:
            body (BoxLiveViewURLParams): Parameters for live view URL.
        Returns:
            BoxLiveViewURLResponse: The response containing the live view URL.
        """
        if body is None:
            body = BoxLiveViewURLParams()
        return self.client.v1.boxes.live_view_url(box_id=self.data.id, **body)

    def web_terminal(self, body: Optional[BoxWebTerminalURLParams] = None) -> BoxWebTerminalURLResponse:
        """
        Get the web terminal URL for the box.

        Args:
            body (BoxWebTerminalURLParams): Parameters for web terminal URL.
        Returns:
            BoxWebTerminalURLResponse: The response containing the web terminal URL.
        """
        if body is None:
            body = BoxWebTerminalURLParams()
        return self.client.v1.boxes.web_terminal_url(box_id=self.data.id, **body)
