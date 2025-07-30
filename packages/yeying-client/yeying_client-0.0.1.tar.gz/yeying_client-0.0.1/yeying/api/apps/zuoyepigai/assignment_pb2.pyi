from yeying.api.common import message_pb2 as _message_pb2
from yeying.api.apps.zuoyepigai import imagecontent_pb2 as _imagecontent_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import (
    ClassVar as _ClassVar,
    Iterable as _Iterable,
    Mapping as _Mapping,
    Optional as _Optional,
    Union as _Union,
)

DESCRIPTOR: _descriptor.FileDescriptor

class AssignmentUploadRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AssignmentUploadRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AssignmentUploadRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AssignmentUploadRequestBody(_message.Message):
    __slots__ = ("did", "fileUrl", "taskUid", "type", "subject", "testPaperName")
    DID_FIELD_NUMBER: _ClassVar[int]
    FILEURL_FIELD_NUMBER: _ClassVar[int]
    TASKUID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    TESTPAPERNAME_FIELD_NUMBER: _ClassVar[int]
    did: str
    fileUrl: _containers.RepeatedScalarFieldContainer[str]
    taskUid: str
    type: _imagecontent_pb2.ImageContentTypeEnum
    subject: str
    testPaperName: str
    def __init__(
        self,
        did: _Optional[str] = ...,
        fileUrl: _Optional[_Iterable[str]] = ...,
        taskUid: _Optional[str] = ...,
        type: _Optional[_Union[_imagecontent_pb2.ImageContentTypeEnum, str]] = ...,
        subject: _Optional[str] = ...,
        testPaperName: _Optional[str] = ...,
    ) -> None: ...

class AssignmentUploadResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AssignmentUploadResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AssignmentUploadResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AssignmentUploadResponseBody(_message.Message):
    __slots__ = ("status", "result")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    result: str
    def __init__(
        self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ..., result: _Optional[str] = ...
    ) -> None: ...

class AssignmentBigModelRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AssignmentBigModelRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AssignmentBigModelRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AssignmentBigModelRequestBody(_message.Message):
    __slots__ = ("question",)
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    question: str
    def __init__(self, question: _Optional[str] = ...) -> None: ...

class AssignmentBigModelResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AssignmentBigModelResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AssignmentBigModelResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AssignmentBigModelResponseBody(_message.Message):
    __slots__ = ("status", "result")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    result: str
    def __init__(
        self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ..., result: _Optional[str] = ...
    ) -> None: ...

class AssignmentArtificialRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AssignmentArtificialRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AssignmentArtificialRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AssignmentArtificialRequestBody(_message.Message):
    __slots__ = ("fileUrl",)
    FILEURL_FIELD_NUMBER: _ClassVar[int]
    fileUrl: str
    def __init__(self, fileUrl: _Optional[str] = ...) -> None: ...

class AssignmentArtificialResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AssignmentArtificialResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AssignmentArtificialResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AssignmentArtificialResponseBody(_message.Message):
    __slots__ = ("status", "result")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    result: str
    def __init__(
        self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ..., result: _Optional[str] = ...
    ) -> None: ...

class StudentActionRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: StudentActionRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[StudentActionRequestBody, _Mapping]] = ...,
    ) -> None: ...

class StudentActionRequestBody(_message.Message):
    __slots__ = ("taskUid", "did", "action")
    TASKUID_FIELD_NUMBER: _ClassVar[int]
    DID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    taskUid: str
    did: str
    action: str
    def __init__(
        self, taskUid: _Optional[str] = ..., did: _Optional[str] = ..., action: _Optional[str] = ...
    ) -> None: ...

class StudentActionResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: StudentActionResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[StudentActionResponseBody, _Mapping]] = ...,
    ) -> None: ...

class StudentActionResponseBody(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    def __init__(self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ...) -> None: ...

class AssignmentCorrectionRequest(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AssignmentCorrectionRequestBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AssignmentCorrectionRequestBody, _Mapping]] = ...,
    ) -> None: ...

class AssignmentCorrectionRequestBody(_message.Message):
    __slots__ = ("qa",)
    QA_FIELD_NUMBER: _ClassVar[int]
    qa: str
    def __init__(self, qa: _Optional[str] = ...) -> None: ...

class AssignmentCorrectionResponse(_message.Message):
    __slots__ = ("header", "body")
    HEADER_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    header: _message_pb2.MessageHeader
    body: AssignmentCorrectionResponseBody
    def __init__(
        self,
        header: _Optional[_Union[_message_pb2.MessageHeader, _Mapping]] = ...,
        body: _Optional[_Union[AssignmentCorrectionResponseBody, _Mapping]] = ...,
    ) -> None: ...

class AssignmentCorrectionResponseBody(_message.Message):
    __slots__ = ("status", "result")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    status: _message_pb2.ResponseStatus
    result: str
    def __init__(
        self, status: _Optional[_Union[_message_pb2.ResponseStatus, _Mapping]] = ..., result: _Optional[str] = ...
    ) -> None: ...
