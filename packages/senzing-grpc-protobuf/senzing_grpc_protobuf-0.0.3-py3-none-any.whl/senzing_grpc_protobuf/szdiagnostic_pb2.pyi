from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CheckRepositoryPerformanceRequest(_message.Message):
    __slots__ = ("seconds_to_run",)
    SECONDS_TO_RUN_FIELD_NUMBER: _ClassVar[int]
    seconds_to_run: int
    def __init__(self, seconds_to_run: _Optional[int] = ...) -> None: ...

class CheckRepositoryPerformanceResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetRepositoryInfoRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetRepositoryInfoResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetFeatureRequest(_message.Message):
    __slots__ = ("feature_id",)
    FEATURE_ID_FIELD_NUMBER: _ClassVar[int]
    feature_id: int
    def __init__(self, feature_id: _Optional[int] = ...) -> None: ...

class GetFeatureResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class PurgeRepositoryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PurgeRepositoryResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReinitializeRequest(_message.Message):
    __slots__ = ("config_id",)
    CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    config_id: int
    def __init__(self, config_id: _Optional[int] = ...) -> None: ...

class ReinitializeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
