# -*- coding:utf-8 -*-
import uuid

from google.protobuf.json_format import MessageToJson
from yeying.api.asset import recycle_pb2, link_pb2_grpc, link_pb2, LinkTypeEnum
from yeying.api.common import ResponseCodeEnum, message_pb2
from yeying.client.provider.base_provider import BaseProvider
import grpc
from yeying.client.utils import log_utils
from yeying.client.utils.date_utils import get_current_utc_string, plus_second, get_current_utc_datetime, to_iso

log = log_utils.get_logger(__name__)


"""
LinkProvider 类提供对资产分享链接的管理
"""
class LinkProvider(BaseProvider):

    def __init__(self, **kw):
        super(LinkProvider, self).__init__(**kw)
        self.link_client = link_pb2_grpc.LinkStub(grpc.insecure_channel(self.option.proxy))

    def search(self, page, page_size, condition: link_pb2.SearchLinkCondition=None):
        """
        搜索资产分享链接
        :param page:当前页码
        :param page_size:每页显示的条目数
        :param condition:可选，搜索某个资产的分享链接。
        :return:
        """
        body = link_pb2.SearchLinkRequestBody(condition=condition, page=message_pb2.RequestPage(page=page, pageSize=page_size))
        header = self.authenticate.create_header(body=body)
        request = link_pb2.SearchLinkRequest(header=header, body=body)
        response: link_pb2.SearchLinkResponse = self.link_client.Search(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"search error, response={MessageToJson(response)}")
        return response

    def create(
        self,
        namespaceId: str,
        name: str,
        _hash: str,
        duration: int,
        _type: LinkTypeEnum,
        visitors: list[str],
        description: str
    ) -> link_pb2.CreateLinkResponse:
        """
        创建资产分享链接
        :param namespaceId:资产命名空间
        :param name:分享链接的名称
        :param _hash:要分享的资产哈希值
        :param duration:分享链接有效时长，单位是秒
        :param _type:分享链接类型
        :param visitors:指定具体的访问者
        :param description:描述
        :return:
        """
        link = link_pb2.LinkMetadata(
            owner=self.authenticate.get_did(),
            uid=str(uuid.uuid4()),
            type=_type,
            visitors=",".join(visitors) if visitors and len(visitors) > 0 else None,
            namespaceId=namespaceId,
            name=name,
            description=description,
            hash=_hash,
            startedAt=get_current_utc_string(),
            expiredAt=to_iso(plus_second(get_current_utc_datetime(), duration)),
            createdAt=get_current_utc_string()
        )
        link.signature = self.authenticate.sign_data(link.SerializeToString())
        body = link_pb2.CreateLinkRequestBody(link=link)
        header = self.authenticate.create_header(body=body)
        request = link_pb2.CreateLinkRequest(header=header, body=body)
        response: link_pb2.CreateLinkResponse = self.link_client.Create(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"create error, response={MessageToJson(response)}")
        return response

    def detail(self, uid: str) -> link_pb2.LinkDetailResponse:
        """
        获得资产分享链接详情
        :param uid:分享链接唯一ID
        :return:分享链接详情
        """
        body = link_pb2.LinkDetailRequestBody(uid=uid)
        header = self.authenticate.create_header(body=body)
        request = link_pb2.LinkDetailRequest(header=header, body=body)
        response: link_pb2.LinkDetailResponse = self.link_client.Detail(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"detail error, response={MessageToJson(response)}")
        return response

    def disable(self, uid: str) -> link_pb2.DisableLinkResponse:
        """
        取消资产分享
        :param uid:分享链接唯一ID
        :return:分享链接详情
        """
        body = link_pb2.DisableLinkRequestBody(linkId=uid)
        header = self.authenticate.create_header(body=body)
        request = link_pb2.DisableLinkRequest(header=header, body=body)
        response: link_pb2.DisableLinkResponse = self.link_client.Disable(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"disable error, response={MessageToJson(response)}")
        return response

    def visitors(self, uid: str, page: int, page_size: int) -> link_pb2.LinkVisitorResponse:
        """
        获得资产链接访问者
        :param uid:分享链接唯一ID
        :param page:当前页码
        :param page_size:每页显示的条目数
        :return:资产链接访问者列表
        """
        body = link_pb2.LinkVisitorRequestBody(uid=uid, page=message_pb2.RequestPage(page=page, pageSize=page_size))
        header = self.authenticate.create_header(body=body)
        request = link_pb2.LinkVisitorRequest(header=header, body=body)
        response: link_pb2.LinkVisitorResponse = self.link_client.Visitor(request)

        if ResponseCodeEnum.OK != response.body.status.code:
            raise Exception(f"visitors error, response={MessageToJson(response)}")
        return response