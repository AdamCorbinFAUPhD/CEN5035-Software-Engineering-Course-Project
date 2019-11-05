from enum import Enum


class PirEventType(Enum):
    """Enum class to define the different PIR events"""
    falling = 1
    rising = 2


class PIREvent:
    """Class for defining the messages for the PIR Queue in PIR_Sensor class"""
    time: int
    event_type: PirEventType

    def __init__(self, time: float, event_type: PirEventType):
        self.time = time
        self.event_type = event_type



