from typing import Union

from gbox_sdk._client import GboxClient
from gbox_sdk._response import BinaryAPIResponse
from gbox_sdk.types.v1.android_box import AndroidBox
from gbox_sdk.types.v1.boxes.android_app import AndroidApp
from gbox_sdk.types.v1.boxes.android_open_params import AndroidOpenParams
from gbox_sdk.types.v1.boxes.android_restart_params import AndroidRestartParams
from gbox_sdk.types.v1.boxes.android_list_activities_response import AndroidListActivitiesResponse


class AndroidAppOperator:
    """
    Operator class for managing a specific Android app within a box.

    Provides methods to open, restart, close, list activities, and backup the app.

    Attributes:
        client (GboxClient): The API client used for communication.
        box (AndroidBox): The Android box data object.
        data (AndroidApp): The app data object.
    """

    def __init__(self, client: GboxClient, box: AndroidBox, data: AndroidApp):
        """
        Initialize an AndroidAppOperator instance.

        Args:
            client (GboxClient): The API client used for communication.
            box (AndroidBox): The Android box data object.
            data (AndroidApp): The app data object.
        """
        self.client = client
        self.box = box
        self.data = data

    def open(self, activity_name: Union[str, None] = None) -> None:
        """
        Open the app, optionally specifying an activity name.

        Args:
            activity_name (str, optional): The activity name to open. Defaults to None.
        """
        params = AndroidOpenParams(box_id=self.box.id)
        if activity_name is not None:
            params["activity_name"] = activity_name
        return self.client.v1.boxes.android.open(self.data.package_name, **params)

    def restart(self, activity_name: Union[str, None] = None) -> None:
        """
        Restart the app, optionally specifying an activity name.

        Args:
            activity_name (str, optional): The activity name to restart. Defaults to None.
        """
        params = AndroidRestartParams(box_id=self.box.id)
        if activity_name is not None:
            params["activity_name"] = activity_name
        return self.client.v1.boxes.android.restart(self.data.package_name, **params)

    def close(self) -> None:
        """
        Close the app.
        """
        return self.client.v1.boxes.android.close(package_name=self.data.package_name, box_id=self.box.id)

    def list_activities(self) -> AndroidListActivitiesResponse:
        """
        List all activities of the app.

        Returns:
            AndroidListActivitiesResponse: The response containing the list of activities.
        """
        return self.client.v1.boxes.android.list_activities(package_name=self.data.package_name, box_id=self.box.id)

    def backup(self) -> BinaryAPIResponse:
        """
        Backup the app.

        Returns:
            BinaryAPIResponse: The backup response containing binary data.
        """
        return self.client.v1.boxes.android.backup(package_name=self.data.package_name, box_id=self.box.id)
