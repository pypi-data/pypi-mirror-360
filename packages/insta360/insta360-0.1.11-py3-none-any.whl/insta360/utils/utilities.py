import typing as t

from google.protobuf import json_format


def bytes_to_hexascii(bytes_string: bytes) -> str:
    """Convert a bytearray or bytes into a printable string of hex codes and ASCII
    :param bytes_string: bytes to convert
    :type bytes_string: bytes

    :return: converted hex codes and ASCII string
    :rtype: str
    """

    hex_ascii_string = ""
    ascii_ranges = [(" ", "&"), ("(", "["), ("]", "~")]
    for i in range(0, len(bytes_string)):
        b = bytes_string[i]
        is_ascii = False
        for r in ascii_ranges:
            if ord(r[0]) <= b <= ord(r[1]):
                hex_ascii_string += chr(b)
                is_ascii = True
                break
        if not is_ascii:
            hex_ascii_string += "\\x%02x" % b
    return hex_ascii_string


def bytes_to_hex(bytes_string: bytes) -> str:
    """Convert a bytearray or bytes into a string of hex codes
    :param bytes_string: bytes to convert
    :type bytes_string: bytes

    :return: converted hex string
    :rtype: str
    """
    hex_string = ""
    for i in range(0, len(bytes_string)):
        b = bytes_string[i]
        hex_string += "\\x%02x" % b
    return hex_string


def protobuf_to_dict(
    message: t.Any, response_code: int = None, message_code: int = None
) -> t.Dict[t.Any, t.Any]:
    """Converts a protobuf message into a Python dictionary
    :param message: protobuf message
    :type message: protobuf message response type. For ex: set_options_pb2.SetOptionsResp

    :param response_code: protobuf response code
    :type response_code: int

    :param message_code: protobuf message code
    :type message_code: int

    :return: protobuf message parsed to dict
    :rtype: dict
    """
    msg = json_format.MessageToDict(message)
    msg["response_code"] = response_code
    msg["message_code"] = message_code
    return msg
