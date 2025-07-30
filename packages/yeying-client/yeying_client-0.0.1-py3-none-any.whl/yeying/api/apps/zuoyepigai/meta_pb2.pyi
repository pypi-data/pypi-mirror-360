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

class GroupMetaData(_message.Message):
    __slots__ = ("uid", "did", "groupName", "createdAt", "updatedAt", "isDeleted", "teacherDid", "studentName")
    UID_FIELD_NUMBER: _ClassVar[int]
    DID_FIELD_NUMBER: _ClassVar[int]
    GROUPNAME_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    TEACHERDID_FIELD_NUMBER: _ClassVar[int]
    STUDENTNAME_FIELD_NUMBER: _ClassVar[int]
    uid: str
    did: str
    groupName: str
    createdAt: int
    updatedAt: int
    isDeleted: bool
    teacherDid: str
    studentName: str
    def __init__(
        self,
        uid: _Optional[str] = ...,
        did: _Optional[str] = ...,
        groupName: _Optional[str] = ...,
        createdAt: _Optional[int] = ...,
        updatedAt: _Optional[int] = ...,
        isDeleted: bool = ...,
        teacherDid: _Optional[str] = ...,
        studentName: _Optional[str] = ...,
    ) -> None: ...

class ArchiveMetadata(_message.Message):
    __slots__ = (
        "uid",
        "name",
        "studentDid",
        "teacherDid",
        "subject",
        "createdAt",
        "updatedAt",
        "isDeleted",
        "telephone",
        "email",
        "status",
    )
    UID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    STUDENTDID_FIELD_NUMBER: _ClassVar[int]
    TEACHERDID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    TELEPHONE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    uid: str
    name: str
    studentDid: str
    teacherDid: str
    subject: str
    createdAt: int
    updatedAt: int
    isDeleted: bool
    telephone: str
    email: str
    status: str
    def __init__(
        self,
        uid: _Optional[str] = ...,
        name: _Optional[str] = ...,
        studentDid: _Optional[str] = ...,
        teacherDid: _Optional[str] = ...,
        subject: _Optional[str] = ...,
        createdAt: _Optional[int] = ...,
        updatedAt: _Optional[int] = ...,
        isDeleted: bool = ...,
        telephone: _Optional[str] = ...,
        email: _Optional[str] = ...,
        status: _Optional[str] = ...,
    ) -> None: ...

class HomeworkMetadata(_message.Message):
    __slots__ = ("uid", "did", "subject", "testPaperUid", "createdAt", "updatedAt", "isDeleted")
    UID_FIELD_NUMBER: _ClassVar[int]
    DID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    TESTPAPERUID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    uid: str
    did: str
    subject: str
    testPaperUid: str
    createdAt: int
    updatedAt: int
    isDeleted: bool
    def __init__(
        self,
        uid: _Optional[str] = ...,
        did: _Optional[str] = ...,
        subject: _Optional[str] = ...,
        testPaperUid: _Optional[str] = ...,
        createdAt: _Optional[int] = ...,
        updatedAt: _Optional[int] = ...,
        isDeleted: bool = ...,
    ) -> None: ...

class MistakesMetadata(_message.Message):
    __slots__ = ("uid", "question", "answer", "createdAt", "updatedAt", "isDeleted")
    UID_FIELD_NUMBER: _ClassVar[int]
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    uid: str
    question: str
    answer: str
    createdAt: int
    updatedAt: int
    isDeleted: bool
    def __init__(
        self,
        uid: _Optional[str] = ...,
        question: _Optional[str] = ...,
        answer: _Optional[str] = ...,
        createdAt: _Optional[int] = ...,
        updatedAt: _Optional[int] = ...,
        isDeleted: bool = ...,
    ) -> None: ...

class MessageMetadata(_message.Message):
    __slots__ = ("uid", "title", "type", "content", "createdAt", "updatedAt", "isDeleted")
    UID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    uid: str
    title: str
    type: int
    content: str
    createdAt: int
    updatedAt: int
    isDeleted: bool
    def __init__(
        self,
        uid: _Optional[str] = ...,
        title: _Optional[str] = ...,
        type: _Optional[int] = ...,
        content: _Optional[str] = ...,
        createdAt: _Optional[int] = ...,
        updatedAt: _Optional[int] = ...,
        isDeleted: bool = ...,
    ) -> None: ...

class TaskMetadata(_message.Message):
    __slots__ = (
        "uid",
        "name",
        "description",
        "tagUid",
        "did",
        "studentDidList",
        "createdAt",
        "updatedAt",
        "startTime",
        "endTime",
        "isDeleted",
        "status",
    )
    UID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGUID_FIELD_NUMBER: _ClassVar[int]
    DID_FIELD_NUMBER: _ClassVar[int]
    STUDENTDIDLIST_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    STARTTIME_FIELD_NUMBER: _ClassVar[int]
    ENDTIME_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    uid: str
    name: str
    description: str
    tagUid: str
    did: str
    studentDidList: str
    createdAt: int
    updatedAt: int
    startTime: int
    endTime: int
    isDeleted: bool
    status: _imagecontent_pb2.TaskStatusEnum
    def __init__(
        self,
        uid: _Optional[str] = ...,
        name: _Optional[str] = ...,
        description: _Optional[str] = ...,
        tagUid: _Optional[str] = ...,
        did: _Optional[str] = ...,
        studentDidList: _Optional[str] = ...,
        createdAt: _Optional[int] = ...,
        updatedAt: _Optional[int] = ...,
        startTime: _Optional[int] = ...,
        endTime: _Optional[int] = ...,
        isDeleted: bool = ...,
        status: _Optional[_Union[_imagecontent_pb2.TaskStatusEnum, str]] = ...,
    ) -> None: ...

class TagCountMeta(_message.Message):
    __slots__ = ("tagUid", "tagName", "count")
    TAGUID_FIELD_NUMBER: _ClassVar[int]
    TAGNAME_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    tagUid: str
    tagName: str
    count: int
    def __init__(
        self, tagUid: _Optional[str] = ..., tagName: _Optional[str] = ..., count: _Optional[int] = ...
    ) -> None: ...

class TaskTagMetadata(_message.Message):
    __slots__ = ("uid", "name", "did", "createdAt", "updatedAt", "isDeleted")
    UID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DID_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    uid: str
    name: str
    did: str
    createdAt: int
    updatedAt: int
    isDeleted: bool
    def __init__(
        self,
        uid: _Optional[str] = ...,
        name: _Optional[str] = ...,
        did: _Optional[str] = ...,
        createdAt: _Optional[int] = ...,
        updatedAt: _Optional[int] = ...,
        isDeleted: bool = ...,
    ) -> None: ...

class WarehouseMetadata(_message.Message):
    __slots__ = (
        "uid",
        "did",
        "url",
        "urlMetaData",
        "taskUid",
        "type",
        "createdAt",
        "updatedAt",
        "isDeleted",
        "urlIndex",
    )
    UID_FIELD_NUMBER: _ClassVar[int]
    DID_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    URLMETADATA_FIELD_NUMBER: _ClassVar[int]
    TASKUID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CREATEDAT_FIELD_NUMBER: _ClassVar[int]
    UPDATEDAT_FIELD_NUMBER: _ClassVar[int]
    ISDELETED_FIELD_NUMBER: _ClassVar[int]
    URLINDEX_FIELD_NUMBER: _ClassVar[int]
    uid: str
    did: str
    url: str
    urlMetaData: _containers.RepeatedCompositeFieldContainer[UrlMetaData]
    taskUid: str
    type: _imagecontent_pb2.ImageContentTypeEnum
    createdAt: int
    updatedAt: int
    isDeleted: bool
    urlIndex: int
    def __init__(
        self,
        uid: _Optional[str] = ...,
        did: _Optional[str] = ...,
        url: _Optional[str] = ...,
        urlMetaData: _Optional[_Iterable[_Union[UrlMetaData, _Mapping]]] = ...,
        taskUid: _Optional[str] = ...,
        type: _Optional[_Union[_imagecontent_pb2.ImageContentTypeEnum, str]] = ...,
        createdAt: _Optional[int] = ...,
        updatedAt: _Optional[int] = ...,
        isDeleted: bool = ...,
        urlIndex: _Optional[int] = ...,
    ) -> None: ...

class UrlMetaData(_message.Message):
    __slots__ = ("index", "url")
    INDEX_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    index: int
    url: str
    def __init__(self, index: _Optional[int] = ..., url: _Optional[str] = ...) -> None: ...
