import time

from gbox_sdk import GboxSDK


def main() -> None:
    try:
        print("Initializing GboxSDK...")
        gbox = GboxSDK(
            api_key="gbox_1234567890"
            # base_url="https://gbox.ai/api/v1",  # Add if needed
        )
        print("Initializing android box...")
        box = gbox.create(
            {
                "type": "android",
                "config": {
                    "device_type": "virtual",
                    "envs": {"GITHUB_TOKEN": "ghp_1234567890"},
                    "labels": {"test": "test"},
                },
                "wait": True,
            }
        )
        # box = gbox.get(box_id="9742eb6d-3a0a-4fde-bb29-1e643ab6918a")

        # !important: Please do not delete or modify this code, it is used to get the gbox id
        print("gbox id:", box.data.id)

        time.sleep(2)
        print("Opening message app")
        box.action.click({"x": 230, "y": 1201})
        time.sleep(2)
        print("Clicking Start Chat button")
        box.action.click({"x": 364, "y": 1464})
        time.sleep(3)
        print("Clicking Without login")
        box.action.click({"x": 554, "y": 1418})
        time.sleep(2)
        print("Clicking Start Chat button Again")
        box.action.click({"x": 546, "y": 1414})
        time.sleep(2)
        print("Pressing Home Button")
        box.action.press_key({"keys": ["home"]})
        time.sleep(2)
        print("Clicking on search bar")
        box.action.click({"x": 346, "y": 1379})
        time.sleep(2)
        print("Typing in search bar")
        box.action.type({"text": "gru%sai"})
        time.sleep(2)
        print("Pressing Enter")
        box.action.press_key({"keys": ["enter"]})
        time.sleep(2)
        print(
            "All done. You can continue to use this Android box online, or realize your own creativity via our SDK. ❤"
        )
    except Exception as e:
        print("Caught exception:", e)


if __name__ == "__main__":
    main()
