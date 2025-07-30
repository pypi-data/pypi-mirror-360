from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetDataSourceRegistryRequest(_message.Message):
    __slots__ = ("config_definition",)
    CONFIG_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    config_definition: str
    def __init__(self, config_definition: _Optional[str] = ...) -> None: ...

class GetDataSourceRegistryResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class RegisterDataSourceRequest(_message.Message):
    __slots__ = ("config_definition", "data_source_code")
    CONFIG_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    config_definition: str
    data_source_code: str
    def __init__(self, config_definition: _Optional[str] = ..., data_source_code: _Optional[str] = ...) -> None: ...

class RegisterDataSourceResponse(_message.Message):
    __slots__ = ("result", "config_definition")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    CONFIG_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    result: str
    config_definition: str
    def __init__(self, result: _Optional[str] = ..., config_definition: _Optional[str] = ...) -> None: ...

class UnregisterDataSourceRequest(_message.Message):
    __slots__ = ("config_definition", "data_source_code")
    CONFIG_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_CODE_FIELD_NUMBER: _ClassVar[int]
    config_definition: str
    data_source_code: str
    def __init__(self, config_definition: _Optional[str] = ..., data_source_code: _Optional[str] = ...) -> None: ...

class UnregisterDataSourceResponse(_message.Message):
    __slots__ = ("result", "config_definition")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    CONFIG_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    result: str
    config_definition: str
    def __init__(self, result: _Optional[str] = ..., config_definition: _Optional[str] = ...) -> None: ...

class VerifyConfigRequest(_message.Message):
    __slots__ = ("config_definition",)
    CONFIG_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    config_definition: str
    def __init__(self, config_definition: _Optional[str] = ...) -> None: ...

class VerifyConfigResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    def __init__(self, result: bool = ...) -> None: ...
