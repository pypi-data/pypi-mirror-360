from gbox_sdk._client import GboxClient


class BrowserOperator:
    """
    Provides operations related to browser management for a specific box.

    Args:
        client (GboxClient): The GboxClient instance used to interact with the API.
        box_id (str): The unique identifier of the box.
    """

    def __init__(self, client: GboxClient, box_id: str):
        """
        Initialize a BrowserOperator instance.

        Args:
            client (GboxClient): The GboxClient instance used to interact with the API.
            box_id (str): The unique identifier of the box.
        """
        self.client = client
        self.box_id = box_id

    def cdpUrl(self) -> str:
        """
        Get the Chrome DevTools Protocol (CDP) URL for the browser in the specified box.

        Returns:
            str: The CDP URL for the browser.
        """
        return self.client.v1.boxes.browser.cdp_url(box_id=self.box_id)
