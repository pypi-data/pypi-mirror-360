# -*- coding:utf-8 -*-
from google.protobuf.json_format import MessageToJson
from yeying.api.asset import recycle_pb2_grpc, recycle_pb2, asset_pb2
from yeying.api.common import ResponseCodeEnum, message_pb2
from yeying.client.provider.base_provider import BaseProvider
import grpc
from yeying.client.utils import log_utils

log = log_utils.get_logger(__name__)


"""
资产仓库资源回收站 CURD
"""


class RecycleProvider(BaseProvider):

    def __init__(self, **kw):
        super(RecycleProvider, self).__init__(**kw)
        # 资产元信息
        self.recycle_client = recycle_pb2_grpc.RecycleStub(grpc.insecure_channel(self.option.proxy))

    def search(self, page: int, page_size: int, condition: asset_pb2.SearchAssetCondition) -> recycle_pb2.SearchDeletedAssetResponse:
        body = recycle_pb2.SearchDeletedAssetRequestBody(condition=condition, page=message_pb2.RequestPage(page=page, pageSize=page_size))
        header = self.authenticate.create_header(body=body)
        request = recycle_pb2.SearchDeletedAssetRequest(header=header, body=body)
        response: recycle_pb2.SearchDeletedAssetResponse = self.recycle_client.Search(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"search error, response={MessageToJson(response)}")
        return response

    def recover(
        self, namespace_id: str, _hash: str
    ) -> recycle_pb2.RecoverDeletedAssetResponse:
        body = recycle_pb2.RecoverDeletedAssetRequestBody(hash=_hash, namespaceId=namespace_id)
        header = self.authenticate.create_header(body=body)
        request = recycle_pb2.RecoverDeletedAssetRequest(header=header, body=body)
        response: recycle_pb2.RecoverDeletedAssetResponse = self.recycle_client.Recover(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"recover error, response={MessageToJson(response)}")
        return response

    def remove(self, namespace_id: str, _hash: str) -> recycle_pb2.RemoveDeletedAssetResponse:
        body = recycle_pb2.RemoveDeletedAssetRequestBody(hash=_hash, namespaceId=namespace_id)
        header = self.authenticate.create_header(body=body)
        request = recycle_pb2.RemoveDeletedAssetRequest(header=header, body=body)
        response: recycle_pb2.RemoveDeletedAssetResponse = self.recycle_client.Remove(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"remove error, response={MessageToJson(response)}")
        return response
