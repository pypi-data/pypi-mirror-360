from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetConfigRequest(_message.Message):
    __slots__ = ("config_id",)
    CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    config_id: int
    def __init__(self, config_id: _Optional[int] = ...) -> None: ...

class GetConfigResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetConfigRegistryRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetConfigRegistryResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class GetDefaultConfigIdRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetDefaultConfigIdResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class GetTemplateConfigRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetTemplateConfigResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: str
    def __init__(self, result: _Optional[str] = ...) -> None: ...

class RegisterConfigRequest(_message.Message):
    __slots__ = ("config_definition", "config_comment")
    CONFIG_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    CONFIG_COMMENT_FIELD_NUMBER: _ClassVar[int]
    config_definition: str
    config_comment: str
    def __init__(self, config_definition: _Optional[str] = ..., config_comment: _Optional[str] = ...) -> None: ...

class RegisterConfigResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class ReplaceDefaultConfigIdRequest(_message.Message):
    __slots__ = ("current_default_config_id", "new_default_config_id")
    CURRENT_DEFAULT_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_DEFAULT_CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    current_default_config_id: int
    new_default_config_id: int
    def __init__(self, current_default_config_id: _Optional[int] = ..., new_default_config_id: _Optional[int] = ...) -> None: ...

class ReplaceDefaultConfigIdResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class SetDefaultConfigRequest(_message.Message):
    __slots__ = ("config_definition", "config_comment")
    CONFIG_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    CONFIG_COMMENT_FIELD_NUMBER: _ClassVar[int]
    config_definition: str
    config_comment: str
    def __init__(self, config_definition: _Optional[str] = ..., config_comment: _Optional[str] = ...) -> None: ...

class SetDefaultConfigResponse(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: int
    def __init__(self, result: _Optional[int] = ...) -> None: ...

class SetDefaultConfigIdRequest(_message.Message):
    __slots__ = ("config_id",)
    CONFIG_ID_FIELD_NUMBER: _ClassVar[int]
    config_id: int
    def __init__(self, config_id: _Optional[int] = ...) -> None: ...

class SetDefaultConfigIdResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
