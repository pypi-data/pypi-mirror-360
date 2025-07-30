from typing import Union
from typing_extensions import Required, TypedDict

from gbox_sdk.types.v1.boxes.android_install_params import InstallAndroidPkgByURL, InstallAndroidPkgByFile


class InstallAndroidAppByLocalFile(TypedDict, total=False):
    apk: Required[str]


AndroidInstall = Union[InstallAndroidPkgByFile, InstallAndroidPkgByURL, InstallAndroidAppByLocalFile]
