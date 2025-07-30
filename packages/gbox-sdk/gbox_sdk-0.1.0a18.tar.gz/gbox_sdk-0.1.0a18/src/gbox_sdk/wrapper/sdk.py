from typing import Any, List, Union, Mapping, Optional, cast, overload
from typing_extensions import Literal, TypedDict

import httpx

from gbox_sdk import GboxClient
from gbox_sdk._types import NOT_GIVEN, Timeout, NotGiven
from gbox_sdk.wrapper.utils import is_linux_box, is_android_box
from gbox_sdk.wrapper.box.linux import LinuxBoxOperator
from gbox_sdk.types.v1.linux_box import LinuxBox
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.types.v1.box_list_response import BoxListResponse
from gbox_sdk.wrapper.box.android.android import AndroidBoxOperator
from gbox_sdk.types.v1.box_retrieve_response import BoxRetrieveResponse
from gbox_sdk.types.v1.box_create_linux_params import Config as LinuxConfig, BoxCreateLinuxParams
from gbox_sdk.types.v1.box_create_android_params import Config as AndroidConfig, BoxCreateAndroidParams

BoxOperator = Union[AndroidBoxOperator, LinuxBoxOperator]


class _CreateAndroidRequired(TypedDict):
    """Required fields for CreateAndroid."""
    type: Literal["android"]


class _CreateAndroidOptional(TypedDict, total=False):
    """Optional fields for CreateAndroid."""
    config: AndroidConfig
    wait: bool


class CreateAndroid(_CreateAndroidRequired, _CreateAndroidOptional):
    """Parameters for creating an Android box with type specification."""
    pass


class _CreateLinuxRequired(TypedDict):
    """Required fields for CreateLinux."""
    type: Literal["linux"]


class _CreateLinuxOptional(TypedDict, total=False):
    """Optional fields for CreateLinux."""
    config: LinuxConfig
    wait: bool


class CreateLinux(_CreateLinuxRequired, _CreateLinuxOptional):
    """Parameters for creating a Linux box with type specification."""
    pass


CreateParams = Union[CreateAndroid, CreateLinux]


class BoxTerminate(TypedDict, total=False):
    """Parameters for terminating a box."""
    pass


class BoxList(TypedDict, total=False):
    """Parameters for listing boxes."""
    pass


class BoxListOperatorResponse:
    def __init__(
        self,
        operators: List[BoxOperator],
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        total: Optional[int] = None,
    ):
        self.operators = operators
        self.page = page
        self.page_size = page_size
        self.total = total


class GboxSDK:
    """
    GboxSDK provides a high-level interface for managing and operating Gbox containers (boxes).

    This SDK allows users to create, list, retrieve, and terminate both Android and Linux boxes, and provides
    operator objects for further box-specific operations. It wraps the lower-level GboxClient and exposes
    convenient methods for common workflows.

    Attributes:
        client (GboxClient): The underlying client used for API communication.

    Examples:
        Initialize the SDK:
        ```python
        from gbox_sdk.wrapper import GboxSDK

        # Initialize the SDK
        sdk = GboxSDK(api_key="your-api-key")
        ```

        Create boxes using the unified create method:
        ```python
        # Create an Android box
        android_box = sdk.create({
            'type': 'android',
            'config': {'labels': {'env': 'test'}}
        })

        # Create a Linux box
        linux_box = sdk.create({
            'type': 'linux',
            'config': {'envs': {'PYTHON_VERSION': '3.9'}}
        })
        ```

        List and manage boxes:
        ```python
        # List all boxes
        boxes = sdk.list()

        # Get a specific box
        box = sdk.get('box_id')

        # Terminate a box
        sdk.terminate('box_id')
        ```
    """

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[Union[str, httpx.URL]] = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: Optional[int] = None,
        default_headers: Optional[Mapping[str, str]] = None,
        default_query: Optional[Mapping[str, object]] = None,
        http_client: Optional[httpx.Client] = None,
        _strict_response_validation: Optional[bool] = None,
    ):
        """
        Initialize the GboxSDK instance.

        Args:
            api_key (Optional[str]): API key for authentication.
            base_url (Optional[Union[str, httpx.URL]]): Base URL for the API.
            timeout (Union[float, Timeout, None, NotGiven]): Request timeout setting.
            max_retries (Optional[int]): Maximum number of retries for failed requests.
            default_headers (Optional[Mapping[str, str]]): Default headers to include in requests.
            default_query (Optional[Mapping[str, object]]): Default query parameters for requests.
            http_client (Optional[httpx.Client]): Custom HTTP client instance.
            _strict_response_validation (Optional[bool]): Whether to strictly validate API responses.
        """
        self.client = GboxClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries if max_retries is not None else 2,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation
            if _strict_response_validation is not None
            else False,
        )

    @overload
    def create(self, body: CreateAndroid) -> AndroidBoxOperator:
        """Create a new Android box and return its operator."""
        ...

    @overload
    def create(self, body: CreateLinux) -> LinuxBoxOperator:
        """Create a new Linux box and return its operator."""
        ...

    def create(self, body: CreateParams) -> BoxOperator:
        """
        Create a new box and return its operator.

        This method provides a unified interface for creating both Android and Linux boxes.
        The box type is determined by the 'type' field in the body parameter.

        Args:
            body (CreateParams): Parameters for creating the box. Must include a 'type' field
                                specifying either 'android' or 'linux'.

        Returns:
            BoxOperator: Operator for the created box (AndroidBoxOperator or LinuxBoxOperator).

        Raises:
            ValueError: If an unsupported box type is provided.

        Examples:
            Create an Android box:
            ```python
            android_box = sdk.create({
                'type': 'android',
                'config': {'labels': {'env': 'test'}}
            })
            ```

            Create a Linux box:
            ```python
            linux_box = sdk.create({
                'type': 'linux',
                'config': {'envs': {'PYTHON_VERSION': '3.9'}}
            })
            ```
        """
        box_type = body.get("type")
        if box_type == "android":
            # Build android params preserving types
            android_params = BoxCreateAndroidParams()
            if "config" in body:
                android_params["config"] = body["config"]  # type: ignore
            if "wait" in body:
                android_params["wait"] = body["wait"]  # type: ignore
            android_res = self.client.v1.boxes.create_android(**android_params)
            return AndroidBoxOperator(self.client, android_res)
        elif box_type == "linux":
            # Build linux params preserving types
            linux_params = BoxCreateLinuxParams()
            if "config" in body:
                linux_params["config"] = body["config"]  # type: ignore
            if "wait" in body:
                linux_params["wait"] = body["wait"]  # type: ignore
            linux_res = self.client.v1.boxes.create_linux(**linux_params)
            return LinuxBoxOperator(self.client, linux_res)
        else:
            raise ValueError(f"Unsupported box type: {box_type}")

    def list_info(self, query: Optional[BoxList] = None) -> BoxListResponse:
        """
        List information of all boxes matching the query.

        Args:
            query (Optional[BoxList]): Query parameters for listing boxes.

        Returns:
            BoxListResponse: Response containing box information.

        Examples:
            ```python
            # List all boxes
            boxes = sdk.list_info()

            # List with pagination
            boxes = sdk.list_info({
                'page': 1,
                'page_size': 10
            })
            ```
        """
        if query is None:
            query = BoxList()
        return self.client.v1.boxes.list(**query)

    def list(self, query: Optional[BoxList] = None) -> BoxListOperatorResponse:
        """
        List all boxes matching the query and return their operator objects.

        Args:
            query (Optional[BoxList]): Query parameters for listing boxes.

        Returns:
            BoxListOperatorResponse: Response containing operator objects and pagination info.

        Examples:
            ```python
            # List all boxes
            boxes = sdk.list()

            # List with pagination
            boxes = sdk.list({
                'page': 1,
                'page_size': 10
            })
            ```
        """
        if query is None:
            query = BoxList()
        res = self.client.v1.boxes.list(**query)
        data = getattr(res, "data", [])
        operators = [self.data_to_operator(item) for item in data]
        return BoxListOperatorResponse(
            operators=operators,
            page=getattr(res, "page", None),
            page_size=getattr(res, "page_size", None),
            total=getattr(res, "total", None),
        )

    def get_info(self, box_id: str) -> BoxRetrieveResponse:
        """
        Retrieve detailed information for a specific box.

        Args:
            box_id (str): The ID of the box to retrieve.

        Returns:
            BoxRetrieveResponse: Detailed information about the box.

        Example:
            ```python
            box_info = sdk.get_info('975fed9f-bb28-4718-a2c5-e01f72864bd1')
            ```
        """
        return self.client.v1.boxes.retrieve(box_id)

    def get(self, box_id: str) -> BoxOperator:
        """
        Retrieve a specific box and return its operator object.

        Args:
            box_id (str): The ID of the box to retrieve.

        Returns:
            BoxOperator: Operator object for the specified box.

        Example:
            ```python
            box = sdk.get('975fed9f-bb28-4718-a2c5-e01f72864bd1')
            ```
        """
        res = self.client.v1.boxes.retrieve(box_id)
        return self.data_to_operator(res)

    def terminate(self, box_id: str, body: Optional[BoxTerminate] = None) -> None:
        """
        Terminate a specific box.

        Args:
            box_id (str): The ID of the box to terminate.
            body (Optional[BoxTerminate]): Additional parameters for termination.

        Example:
            ```python
            sdk.terminate('box_id')
            ```
        """
        if body is None:
            body = BoxTerminate()
        self.client.v1.boxes.terminate(box_id, **body)

    def data_to_operator(self, data: Union[AndroidBox, LinuxBox]) -> BoxOperator:
        """
        Convert box data to the corresponding operator object.

        Args:
            data (Union[AndroidBox, LinuxBox]): The box data to convert.

        Returns:
            BoxOperator: The corresponding operator object.

        Raises:
            ValueError: If the box type is invalid.
        """
        if is_android_box(data):
            data_dict = data.model_dump(by_alias=True)
            if (
                "config" in data_dict
                and isinstance(data_dict["config"], dict)
                and cast("dict[str, Any]", data_dict["config"]).get("labels") is None
            ):
                data_dict["config"]["labels"] = {}
            android_box: AndroidBox = AndroidBox(**data_dict)
            return AndroidBoxOperator(self.client, android_box)
        elif is_linux_box(data):
            data_dict = data.model_dump(by_alias=True)
            if (
                "config" in data_dict
                and isinstance(data_dict["config"], dict)
                and cast("dict[str, Any]", data_dict["config"]).get("labels") is None
            ):
                data_dict["config"]["labels"] = {}
            linux_box: LinuxBox = LinuxBox(**data_dict)
            return LinuxBoxOperator(self.client, linux_box)
        else:
            raise ValueError(f"Invalid box type: {data.type}")

    def get_client(self) -> GboxClient:
        """
        Get the underlying GboxClient instance.

        Returns:
            GboxClient: The underlying client instance.
        """
        return self.client
