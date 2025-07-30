import struct

from labels.config.logger import LOGGER


def htonl(val: int) -> int:
    try:
        # Convert from little-endian (host byte order)
        # to big-endian (network byte order)
        return struct.unpack(">i", struct.pack("<i", val))[0]
    except struct.error as exc:
        LOGGER.error("Failed to convert integer: %s", exc)
        return 0


def htonlu(val: int) -> int:
    try:
        # Convert from little-endian (host byte order)
        # to big-endian (network byte order)
        return struct.unpack(">I", struct.pack("<I", val))[0]
    except struct.error as exc:
        LOGGER.error("Failed to convert unsigned integer: %s", exc)
        return 0
