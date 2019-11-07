from enum import Enum


class PirEventType(Enum):
    """
    Enum class to define the different PIR events

    Attributes
    ----------
    falling - the event when the state goes from High -> Low
    rising - the event when the state goes from Low -> High
    """
    falling = 1
    rising = 2


class PIREvent:
    """
    Class for defining the messages for the PIR Queue in PIR_Sensor class

    Attributes
    ----------
    time : float
        representation of when the even want triggered using time.time()
    event_type : PirEventType
        packaging which kind of event was triggered

    """
    time: float
    event_type: PirEventType

    def __init__(self, time: float, event_type: PirEventType):
        self.time = time
        self.event_type = event_type
