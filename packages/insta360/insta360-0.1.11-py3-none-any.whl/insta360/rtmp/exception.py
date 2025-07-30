class CommandFailedException(Exception):
    pass


class CameraNotConnectedException(Exception):
    def __init__(self):
        super().__init__("This device is not connected to the camera wifi")
