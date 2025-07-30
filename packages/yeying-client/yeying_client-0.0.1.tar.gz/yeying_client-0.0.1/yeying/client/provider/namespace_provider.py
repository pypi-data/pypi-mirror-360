# -*- coding:utf-8 -*-
import uuid

from google.protobuf.json_format import MessageToJson

from yeying.client.provider.config_provider import ConfigProvider
from yeying.client.utils.date_utils import get_current_utc_string

from yeying.api.asset import namespace_pb2_grpc, namespace_pb2, SearchNamespaceCondition
from yeying.api.common import ResponseCodeEnum, message_pb2
from yeying.client.provider.base_provider import BaseProvider
from yeying.api.config import config_pb2
import grpc
from yeying.client.utils import log_utils

log = log_utils.get_logger(__name__)


"""
资产仓库资源管理空间 CURD
"""


class NamespaceProvider(BaseProvider):

    def __init__(self, **kw):
        super(NamespaceProvider, self).__init__(**kw)
        # 资产元信息
        self.namespace_client = namespace_pb2_grpc.NamespaceStub(grpc.insecure_channel(self.option.proxy))
        # 字典配置
        self.config_provider = ConfigProvider(option=self.option)

    def get_default_namespace(self) -> str:
        config_res: config_pb2.GetConfigResponse = self.config_provider.get(key="namespace.default", config_type=config_pb2.ConfigTypeEnum.CONFIG_TYPE_USER)
        return config_res.body.config.value

    def set_default_namespace(self, namespace_id: str) -> config_pb2.SetConfigResponse:
        return self.config_provider.set(key="namespace.default", value=namespace_id)

    def search(self, page: int, page_size: int, condition: SearchNamespaceCondition) -> namespace_pb2.SearchNamespaceResponse:
        body = namespace_pb2.SearchNamespaceRequestBody(condition=condition, page=message_pb2.RequestPage(page=page, pageSize=page_size))
        header = self.authenticate.create_header(body=body)
        request = namespace_pb2.SearchNamespaceRequest(header=header, body=body)
        response: namespace_pb2.SearchNamespaceResponse = self.namespace_client.Search(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"search error, response={MessageToJson(response)}")
        return response

    def detail(
        self, uid: str
    ) -> namespace_pb2.NamespaceDetailResponse:
        if not uid:
            raise ValueError("uid is None")
        body = namespace_pb2.NamespaceDetailRequestBody(uid=uid)
        header = self.authenticate.create_header(body=body)
        request = namespace_pb2.NamespaceDetailRequest(header=header, body=body)
        response: namespace_pb2.NamespaceDetailResponse = self.namespace_client.Detail(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"detail error, response={MessageToJson(response)}")
        return response

    def delete(self, uid: str) -> namespace_pb2.DeleteNamespaceResponse:
        body = namespace_pb2.DeleteNamespaceRequestBody(uid=uid)
        header = self.authenticate.create_header(body=body)
        request = namespace_pb2.DeleteNamespaceRequest(header=header, body=body)
        response: namespace_pb2.DeleteNamespaceResponse = self.namespace_client.Delete(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"delete error, response={MessageToJson(response)}")
        return response

    def create(self, name: str, description: str, uid: str=None, participants: str=None) -> namespace_pb2.CreateNamespaceResponse:
        if not name:
            raise ValueError("name is None")
        namespace = namespace_pb2.NamespaceMetadata(
            owner=self.authenticate.get_did(),
            participants=participants,
            uid=uid if uid else str(uuid.uuid4()),
            name=name,
            description=description,
            createdAt=get_current_utc_string(),
            updatedAt=get_current_utc_string(),
        )
        namespace.signature = self.authenticate.sign_data(namespace.SerializeToString())
        body = namespace_pb2.CreateNamespaceRequestBody(
            namespace=namespace
        )

        header = self.authenticate.create_header(body=body)
        request = namespace_pb2.CreateNamespaceRequest(header=header, body=body)
        response: namespace_pb2.CreateNamespaceResponse = self.namespace_client.Create(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"create error, response={MessageToJson(response)}")
        return response