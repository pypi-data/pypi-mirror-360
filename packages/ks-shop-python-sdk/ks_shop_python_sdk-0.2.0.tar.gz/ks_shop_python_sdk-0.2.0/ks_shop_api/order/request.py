# -*- coding: utf-8 -*-
import deprecation
from ks_shop_api.base import RestApi
"""
订单 API
"""


class OpenOrderAddressAuditApproveRequest(RestApi):
    """
    商家同意买家修改地址申请
    更新时间: 2024-03-13 17:04:01
    1.订单已支付后&发货前买家可申请修改收货地址，买家6小时内申请由平台自动审核，买家6小时后申请由商家审核。不支持定金预售订单
    2.操作此API前，需要先从订单详情API中获取地址审核状态，已审核的订单请勿重复操作
    3.仅允许主品订单id操作
    4.订单收货地址变更场景见《订单解决方案》

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.address.audit.approve&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.address.audit.approve"


class OpenOrderAddressAuditRejectRequest(RestApi):
    """
    商家拒绝买家修改地址申请
    更新时间: 2023-11-01 15:19:24
    1.订单已支付后&发货前买家可申请修改收货地址，买家6小时内申请由平台自动审核，买家6小时后申请由商家审核。不支持定金预售订单
    2.操作此API前，需要先从订单详情API中获取地址审核状态，已审核的订单请勿重复操作
    3.订单收货地址变更场景见《订单解决方案》

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.address.audit.reject&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.address.audit.reject"


class OpenOrderAddressUpdateRequest(RestApi):
    """
    商家更改订单收货地址
    更新时间: 2024-01-09 15:56:26
    1.支持商家修改待发货状态的订单收货地址，支持增量更新和全量更新；不支持其他状态的订单以及定金预售订单修改地址；
    2.全量更新时所有字段都必传，增量更新时可以只传有更新的字段；
    3.收货地址为级联关系，因此若收货地址的任何一级有更新，收货地址的省市区和详细地址字段都必传
    4.若商家变更了收货地址，必须通过此API回传新地址给平台，否则将被发货拦截，订单收货地址变更场景见《订单解决方案》

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.address.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.address.update"


class OpenOrderBuyerOrderListRequest(RestApi):
    """
    筛选买家在店铺的订单列表
    更新时间: 2023-10-31 14:15:51
    通过买家openId获取其在当前店铺的所有订单信息

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.buyer.order.list&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.buyer.order.list"


class OpenOrderCursorListRequest(RestApi):
    """
    获取订单列表
    更新时间: 2025-06-27 15:32:13
    1.获取商家视角的订单列表信息
    2.只允许获取90天内的订单数据
    3.若调用超时，请减少筛选条件，并将orderViewStatus值设置为1后重试

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.cursor.list&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.cursor.list"


class OpenOrderDecryptBatchRequest(RestApi):
    """
    批量解密订单
    更新时间: 2023-10-26 15:50:38
    1.仅用于解密实物发货订单的密文数据为明文
    2.解密额度在商家维度，商家在小店PC端、APP端和API上共享解密额度
    3.商家侧详细解密规则查看【官方公告】快手升级消费者隐私信息加密公告
    4.ISV侧解密常见问题查看FAQ -开放平台-数据安全

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.decrypt.batch&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.decrypt.batch"


class OpenOrderDesensitiseBatchRequest(RestApi):
    """
    批量脱敏订单
    更新时间: 2024-04-19 10:47:39
    根据订单密文信息返回订单脱敏信息，用于脱敏信息展示

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.desensitise.batch&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.desensitise.batch"


class OpenOrderDetailRequest(RestApi):
    """
    获取订单详情
    更新时间: 2025-06-27 14:21:57
    1.获取商家视角的订单详情
    2.主品订单信息和附属的赠品订单信息一起返回
    3.主品订单及其赠品订单有单独的订单id和订单状态，一单一品多数量，只要发货至少一个品，即使未全部发货，状态也会流转到”已发货40“
    4.需要根据主品订单和赠品订单各自的DeliveryInfo.deliveryNum（已发货商品数）和ItemInfo.num（订单商品数）的数量情况来判断主品/赠品订单是否全部发货

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.detail&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.detail"


class OpenOrderEncryptBatchRequest(RestApi):
    """
    批量加密订单
    更新时间: 2024-03-28 20:02:02
    批量加密订单明文信息为密文

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.encrypt.batch&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.encrypt.batch"


class OpenOrderGoodsSplitDeliverRequest(RestApi):
    """
    订单拆单发货
    更新时间: 2024-08-30 16:26:45
    1.支持主品订单、支持赠品订单、支持整单发、支持拆单发，可以完全兼容发货API逻辑
    2.订单为"待发货"状态&&无正在执行的退款&&订单API出参disableDeliveryReasonCode和riskCode没有值时，允许操作订单拆单发货API
    3.主品/赠品订单有各自的订单状态，只要发了订单id下的至少1个商品，订单id下的状态就会推进到”已发货“，赠品订单只可以使用拆单发货接口发货

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.goods.split.deliver&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.goods.split.deliver"


class OpenOrderSearchIndexBatchRequest(RestApi):
    """
    批量获取密文索引串
    更新时间: 2023-10-31 14:21:45
    根据明文信息批量获取密文索引串，可根据密文索引串进行比对合单

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.search.index.batch&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.search.index.batch"


@deprecation.deprecated(details="获取订单列表旗帜（待下线）")
class OpenOrderTagFlagRequest(RestApi):
    """
    获取订单列表旗帜（待下线）
    更新时间: 2023-10-31 14:24:02
    将在10.11号废弃下线，请使用订单列表API直接获取旗帜信息

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.tag.flag&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.tag.flag"


class OpenOrderTakerateInquiryRequest(RestApi):
    """
    订单费率查询
    更新时间: 2023-12-28 15:59:47
    结算侧为开放平台提供计费试算查询服务，帮助商户通过开放平台可以在订单未发生前试查大概的TR收费情况。该试算接口查到的数据唯一等于下单时刻的TR费率，真实收取值还是按订单实际收取为准。

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.order.takerate.inquiry&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.order.takerate.inquiry"


class OpenSellerOrderCloseRequest(RestApi):
    """
    关闭订单
    更新时间: 2023-11-01 14:22:23
    关闭订单，待付款订单可关闭

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.seller.order.close&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.seller.order.close"


class OpenSellerOrderFeeDetailRequest(RestApi):
    """
    获取订单费用详情
    更新时间: 2025-06-06 15:56:07
    获取订单费用详情

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.seller.order.fee.detail&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.seller.order.fee.detail"


class OpenSellerOrderGoodsDeliverRequest(RestApi):
    """
    订单发货
    更新时间: 2024-11-04 12:00:49
    1.只支持整单发货，只支持发主品订单
    2.赠品订单发货需使用拆单发货API
    3.订单为"待发货"状态&&无正在执行的退款&&订单API出参disableDeliveryReasonCode和riskCode没有值时，允许操作订单发货API
    4. 2024年11月25日后，对于使用相同快递单号重复调用该发货接口，会幂等返回发货成功

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.seller.order.goods.deliver&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.seller.order.goods.deliver"


class OpenSellerOrderGoodsLogisticsAppendRequest(RestApi):
    """
    追加包裹
    更新时间: 2024-01-10 15:00:41
    订单追加发货包裹，入参oid只支持主品订单id
    1.普通订单状态为”已发货“后，可以使用追加包裹
    2.主品赠品订单为”已发货“，并且所有主品赠品商品都”全部发货“后，可以使用追加包裹

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.seller.order.goods.logistics.append&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.seller.order.goods.logistics.append"


class OpenSellerOrderLogisticsUpdateRequest(RestApi):
    """
    更新订单物流信息
    更新时间: 2024-06-24 17:31:28
    根据订单id和包裹id更新订单的物流信息，支持主赠订单

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.seller.order.logistics.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.seller.order.logistics.update"


class OpenSellerOrderNoteAddRequest(RestApi):
    """
    添加订单插旗备注
    更新时间: 2024-07-09 15:30:35
    添加订单插旗和备注信息，插旗颜色无法清除，默认GREY，备注为追加逻辑，可添加空备注

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.seller.order.note.add&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.seller.order.note.add"


class OpenSellerOrderSkuUpdateRequest(RestApi):
    """
    修改订单规格信息
    更新时间: 2023-11-01 16:48:44
    根据订单id和商品id修改订单的商品规格信息，需要买家同意后，商家可进行修改

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.seller.order.sku.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.seller.order.sku.update"
