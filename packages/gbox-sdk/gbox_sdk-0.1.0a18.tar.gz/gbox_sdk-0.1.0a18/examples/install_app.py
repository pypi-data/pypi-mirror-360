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
        print("gbox id:", box.data.id)
        time.sleep(2)
        print("Installing app from URL...")
        app = box.app.install(
            {"apk": "https://github.com/appium/appium/raw/master/packages/appium/sample-code/apps/ApiDemos-debug.apk"}
        )
        package_name = app.data.package_name
        print("App installed successfully!")
        time.sleep(2)
        android_app = box.app.get(package_name)
        time.sleep(2)
        print("Opening app...")
        android_app.open()
        print("App opened successfully!")
    except Exception as e:
        print("Caught exception:", e)


if __name__ == "__main__":
    main()
