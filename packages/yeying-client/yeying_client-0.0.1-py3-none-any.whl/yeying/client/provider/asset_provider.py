# -*- coding:utf-8 -*-
from google.protobuf.json_format import MessageToJson

from yeying.api.common import ResponseCodeEnum, message_pb2
from yeying.client.provider.base_provider import BaseProvider
from yeying.api.asset import asset_pb2_grpc, asset_pb2
import grpc
from yeying.client.utils import log_utils
from yeying.client.utils.date_utils import get_current_utc_string

log = log_utils.get_logger(__name__)


"""
提供对资产的管理，包括查询、版本获取、详情查看、删除等操作
"""
class AssetProvider(BaseProvider):

    def __init__(self, **kw):
        super(AssetProvider, self).__init__(**kw)
        # 资产元信息
        self.asset_client = asset_pb2_grpc.AssetStub(grpc.insecure_channel(self.option.proxy))

    def sign(self, asset: asset_pb2.AssetMetadata) -> asset_pb2.SignAssetResponse:
        """
        签名资产元数据，对资产元数据进行签名，并发送签名请求到后端服务。
        :param asset:签约资产元数据
        :returns 返回签名后的资产元数据
        :throws NoPermission 没有权限
        :throws NotFound 资产不存在
        :throws ServiceUnavailable 服务不可用
        """
        asset.signature = self.authenticate.sign_data(asset.SerializeToString())
        body = asset_pb2.SignAssetRequestBody(asset=asset)
        header = self.authenticate.create_header(body=body)
        request = asset_pb2.SignAssetRequest(header=header, body=body)
        response: asset_pb2.SignAssetResponse = self.asset_client.Sign(request)
        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"sign error, response={MessageToJson(response)}")
        return response

    def detail(self, namespace_id: str, _hash: str) -> asset_pb2.AssetDetailResponse:
        """
        查询资产详情，根据命名空间 ID 和哈希值获取资产元数据
        :param namespace_id:命名空间 ID
        :param _hash:资产的哈希值
        :return:返回资产元数据
        """
        body = asset_pb2.AssetDetailRequestBody(hash=_hash, namespaceId=namespace_id)
        header = self.authenticate.create_header(body=body)
        request = asset_pb2.AssetDetailRequest(header=header, body=body)
        response: asset_pb2.AssetDetailResponse = self.asset_client.Detail(request)
        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"detail error, response={MessageToJson(response)}")
        return response

    def search(self, page: int, page_size: int, condition: asset_pb2.SearchAssetCondition=None) -> asset_pb2.SearchAssetResponse:
        """
        搜索资产，根据条件和分页参数查询资产列表
        :param page:当前页码
        :param page_size:每页显示的条目数
        :param condition:搜索条件（部分 `SearchAssetCondition` 对象）
        :return:返回搜索到的资产元数据列表
        """
        body = asset_pb2.SearchAssetRequestBody(condition=condition, page=message_pb2.RequestPage(page=page, pageSize=page_size))
        header = self.authenticate.create_header(body=body)
        request = asset_pb2.SearchAssetRequest(header=header, body=body)
        response: asset_pb2.SearchAssetResponse = self.asset_client.Search(request)
        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"search error, response={MessageToJson(response)}")
        return response

    def update(self, asset: asset_pb2.AssetMetadata) -> asset_pb2.UpdateAssetResponse:
        """
        更新资产的信息。
        :param asset:资产原数据
        :return:
        """
        detail_res: asset_pb2.AssetDetailResponse = self.detail(namespace_id=asset.namespaceId, _hash=asset.hash)
        existing = detail_res.body.asset
        if asset.name:
            existing.name = asset.name
        if asset.description:
            existing.description = asset.description
        if asset.format:
            existing.format = asset.format
        existing.updatedAt = get_current_utc_string()
        existing.signature = self.authenticate.sign_data(existing.SerializeToString())
        body = asset_pb2.UpdateAssetRequestBody(asset=existing)
        header = self.authenticate.create_header(body=body)
        request = asset_pb2.UpdateAssetRequest(header=header, body=body)
        response: asset_pb2.UpdateAssetResponse = self.asset_client.Update(request)
        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"update error, response={MessageToJson(response)}")
        return response

    def delete(self, namespace_id: str, _hash: str) -> asset_pb2.DeleteAssetResponse:
        """
        删除资产，根据命名空间 ID 和哈希值删除资产
        :param namespace_id:命名空间 ID
        :param _hash:资产的哈希值
        :return:无返回
        """
        body = asset_pb2.DeleteAssetRequestBody(hash=_hash, namespaceId=namespace_id)
        header = self.authenticate.create_header(body=body)
        request = asset_pb2.DeleteAssetRequest(header=header, body=body)
        response: asset_pb2.DeleteAssetResponse = self.asset_client.Delete(request)
        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"delete error, response={MessageToJson(response)}")
        return response