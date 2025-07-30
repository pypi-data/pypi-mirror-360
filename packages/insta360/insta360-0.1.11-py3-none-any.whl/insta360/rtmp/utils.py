import platform
import requests

from .exception import CameraNotConnectedException


def is_hwaccel_supported(supported_platforms) -> bool:
    """
    Check if hardware acceleration is supported on the current platform.

    Parameters:
        supported_platforms: List of platform substrings that support hardware acceleration.

    Returns:
        True if hardware acceleration is supported, False otherwise.
    """

    for supported_platform in supported_platforms:
        if supported_platform in platform.platform():
            return True

    return False


def ensure_camera_connected(connect_host: str):
    """
    Check if the device is connected to the camera wifi.

    Parameters:
        connect_host: The camera's IP address.

    Raises:
        CameraNotConnectedException: If the camera is not connected.

    Returns:
        None
    """

    camera_info_url = f"http://{connect_host}/osc/info"
    try:
        r = requests.get(camera_info_url, timeout=20)
        if r.status_code != 200:
            raise CameraNotConnectedException()
    except requests.ConnectionError as e:
        raise CameraNotConnectedException() from e
