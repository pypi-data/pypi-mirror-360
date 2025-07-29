from yta_constants.enum import YTAEnum as Enum


class AudioChannel(Enum):
    """
    Simple Enum class to handle the audio channels
    easier.
    """

    LEFT = -1.0
    RIGHT = 1.0