from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HourlyResult(_message.Message):
    __slots__ = ("UnixTime", "AvgMinuteList")
    UNIXTIME_FIELD_NUMBER: _ClassVar[int]
    AVGMINUTELIST_FIELD_NUMBER: _ClassVar[int]
    UnixTime: int
    AvgMinuteList: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, UnixTime: _Optional[int] = ..., AvgMinuteList: _Optional[_Iterable[float]] = ...) -> None: ...
