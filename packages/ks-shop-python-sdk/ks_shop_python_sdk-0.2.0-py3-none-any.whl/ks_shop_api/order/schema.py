# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, List, Union


class OpenOrderAddressAuditApproveSchema(BaseModel):
    oid: Optional[int] = Field(default=None, description="订单id，仅允许主品订单id，即orderBaseInfo.oid字段")


class OpenOrderAddressAuditRejectSchema(BaseModel):
    oid: Optional[int] = Field(default=None, description="订单id，仅允许主品订单id，即orderBaseInfo.oid字段")


class OpenOrderAddressUpdateSchema(BaseModel):
    consignee: Optional[str] = Field(default=None, description="收货人名称，全量更新必传，增量更新时若不更改收货人人姓名可不传")
    mobile: Optional[str] = Field(default=None, description="收货人手机号，全量更新必传，增量更新时若不更改收货人手机号可不传")
    provinceCode: Optional[int] = Field(default=None, description="省份code，增量更新时若地址有更新必传，查询快手行政区划库API获取code")
    province: Optional[str] = Field(default=None, description="	收货省份，增量更新时若地址有更新必传")
    cityCode: Optional[int] = Field(default=None, description="收货城市code，增量更新时若地址有更新必传，查询快手行政区划库API获取code")
    city: Optional[str] = Field(default=None, description="收货城市，增量更新时若地址有更新必传")
    districtCode: Optional[int] = Field(default=None, description="收货区code，增量更新时若地址有更新必传，查询快手行政区划库API获取code")
    district: Optional[str] = Field(default=None, description="收货区，增量更新时若地址有更新必传")
    address: Optional[str] = Field(default=None, description="收货详细地址，增量更新时若地址有更新必传，若收货地址任何一级有更新，则省市区和详细地址字段都必传")
    orderId: Optional[int] = Field(default=None, description="订单id")
    isPartialUpdate: Optional[bool] = Field(default=None, description="是否部分更新，false-全量更新，true-增量更新")
    town: Optional[str] = Field(default=None, description="收货街道，增量更新时若地址有更新必传")
    townCode: Optional[int] = Field(default=None, description="收货街道code，增量更新时若地址有更新必传，查询快手行政区划库API获取code")


class OpenOrderBuyerOrderListSchema(BaseModel):
    buyerOpenId: Optional[str] = Field(default=None, description="加密后的买家id")
    cursor: Optional[str] = Field(default=None, description="游标")
    limit: Optional[int] = Field(default=None, description="请求条数")
    orderStatus: Optional[List[int]] = Field(default=None, description="订单状态，不填代表全部")
    orderSourceType: Optional[List[int]] = Field(default=None, description="订单来源，自建订单包括（98,99,101），不传代表查询全部")
    startTime: Optional[int] = Field(default=None, description="订单创建的开始时间")
    endTime: Optional[int] = Field(default=None, description="订单创建的结束时间")


class OpenOrderCursorListSchema(BaseModel):
    orderViewStatus: Optional[int] = Field(default=None, description="订单状态，0未知 1 全部 2 待付款 3 待发货 4 待收货（已发货）5 已收货 6 交易成功订单 7 已关闭订单。若此API返回超时，请传入1后重试")
    pageSize: Optional[int] = Field(default=None, description="每页请求数量 最多一页50条")
    sort: Optional[int] = Field(default=None, description="1时间降序 2时间升序 默认降序")
    queryType: Optional[int] = Field(default=None, description="1按创建时间查找 2按更新时间查找 ；默认创建时间，值为1时只允许获取创建时间90天内的订单数据，值为2时仅允许获取更新时间90天内且创建时间240天内的订单数据")
    beginTime: Optional[int] = Field(default=None, description="订单生成时间的开始时间，单位毫秒， 不能小于90天前，且需要小于结束时间")
    endTime: Optional[int] = Field(default=None, description="订单生成时间的截止时间，单位毫秒，与开始时间的时间范围不大于7天")
    cpsType: Optional[int] = Field(default=None, description="分销类型 0-全部 1-普通订单 2-分销订单")
    cursor: Optional[str] = Field(default=None, description="游标内容 第一次传空串，之后传上一次的cursor返回值，若返回“nomore”则标识到底")


class DecryptBaseMetaInfo(BaseModel):
    encryptedData: Optional[str] = Field(default=None, description="密文")
    bizId: Optional[str] = Field(default=None, description="订单号")


class OpenOrderDecryptBatchSchema(BaseModel):
    batchDecryptList: Optional[List[DecryptBaseMetaInfo]] = Field(default=None, description="批量解密list，每次请求，报文条数不超过100条。")


class DesensitiseBaseMetaInfo(BaseModel):
    encryptedData: Optional[str] = Field(default=None, description="密文")
    bizId: Optional[str] = Field(default=None, description="订单号")


class OpenOrderDesensitiseBatchSchema(BaseModel):
    batchDesensitiseList: Optional[List[DesensitiseBaseMetaInfo]] = Field(default=None, description="批量脱敏list，每次请求，报文条数不超过100条。")


class OpenOrderDetailSchema(BaseModel):
    oid: Optional[int] = Field(default=None, description="订单id")


class EncryptBaseMetaInfo(BaseModel):
    decryptedData: Optional[str] = Field(default=None, description="明文")
    bizId: Optional[str] = Field(default=None, description="订单号")
    type: Optional[int] = Field(default=None, description="加密类型 1地址加密 2姓名加密 3电话加密")


class OpenOrderEncryptBatchSchema(BaseModel):
    batchEncryptList: Optional[List[EncryptBaseMetaInfo]] = Field(default=None, description="明文list，每次请求，报文条数不超过100条。")


class SplitDeliveryGoodsOrderItemDTO(BaseModel):
    deliveryNum: Optional[int] = Field(default=None, description="发货商品件数，oid对应的订单下的商品的发货数量，值必须大于等于1且小于等于剩余未发货的商品数")
    oid: Optional[int] = Field(default=None, description="发货订单id，主品订单id或赠品订单id")
    serialNumberList: Optional[List[str]] = Field(default=None, description="SN码列表，30位以内字符，当订单API出参orderDeliveryInfo.serialNumberInfo.serialType（商品码类型）值包含[1]时，发货必传SN码")
    imeiList: Optional[List[str]] = Field(default=None, description="IMEI码列表，15-17位数字，当订单API出参orderDeliveryInfo.serialNumberInfo.serialType（商品码类型）值包含[2]时，发货必传IMEI码")

class SplitDeliveryGoodsPackageItemDTO(BaseModel):
    deliveryGoodsInfoList: Optional[List[SplitDeliveryGoodsOrderItemDTO]] = Field(default=None, description="发货货品信息")
    expressCode: Optional[int] = Field(default=None, description="物流公司code")
    expressNo: Optional[str] = Field(default=None, description="运单号")


class SplitDeliveryGoodsStatusRequest(BaseModel):
    oid: Optional[int] = Field(default=None, description="订单号")
    confirmDeliveryStatus: Optional[int] = Field(default=None, description="	由商家确认的发货状态。10-部分发货、40-全部发货")


class OpenOrderGoodsSplitDeliverSchema(BaseModel):
    mainOrderId: Optional[int] = Field(default=None, description="主订单id值")
    deliveryItemInfoList: Optional[List[SplitDeliveryGoodsPackageItemDTO]] = Field(default=None, description="发货信息")
    deliveryStatus: Optional[List[SplitDeliveryGoodsStatusRequest]] = Field(default=None, description="发货状态")


class IndexParamData(BaseModel):
    plainText: Optional[str] = Field(default=None, description="明文")
    type: Optional[int] = Field(default=None, description="加密类型 1地址加密 2姓名加密 3电话加密")


class OpenOrderSearchIndexBatchSchema(BaseModel):
    indexParamList: Optional[List[IndexParamData]] = Field(default=None, description="批量检索参数列表，每次请求，报文条数不超过100条")


class OpenOrderTagFlagSchema(BaseModel):
    orderViewStatus: Optional[int] = Field(default=None, description="订单状态，0未知 1 全部 2 待付款 3 待发货 4 待收货（已发货）5 已收货 6 交易成功订单 7 已关闭订单")
    pageSize: Optional[int] = Field(default=None, description="每页请求数量 最多一页50条")
    sort: Optional[int] = Field(default=None, description="1时间降序 2时间升序 默认降序")
    queryType: Optional[int] = Field(default=None, description="1按创建时间查找 2按更新时间查找 默认创建时间")
    beginTime: Optional[int] = Field(default=None, description="订单生成时间的开始时间，单位毫秒，不能小于90天前，且需要小于结束时间")
    endTime: Optional[int] = Field(default=None, description="订单生成时间的截止时间，单位毫秒，与开始时间的时间范围不大于7天")
    cpsType: Optional[int] = Field(default=None, description="分销类型 0-全部 1-普通订单 2-分销订单")
    cursor: Optional[str] = Field(default=None, description="游标内容 第一次传空串，之后传上一次的cursor返回值，若返回“nomore”则标识到底")


class OpenOrderTakerateInquirySchema(BaseModel):
    orderTime: Optional[int] = Field(default=None, description="时间戳格式")
    params: Optional[dict] = Field(default=None, description="categoryId、merchantShopType分别为，商品类目id、店铺类型")


class OpenSellerOrderCloseSchema(BaseModel):
    orderId: Optional[int] = Field(default=None, description="订单编号")


class OpenSellerOrderFeeDetailSchema(BaseModel):
    orderId: Optional[int] = Field(default=None, description="订单编号")


class OpenSellerOrderGoodsDeliverSchema(BaseModel):
    returnAddressId: Optional[int] = Field(default=None, description="商家退货地址，可从查询商家地址列表API-open.address.seller.list中获取退货地址")
    qualityParam: Optional[str] = Field(default=None, description="质检信息专用非必填，发货可忽略")
    expressNo: Optional[str] = Field(default=None, description="快递单号")
    expressCode: Optional[int] = Field(default=None, description="快递公司code，由快递公司编码获取")
    orderId: Optional[int] = Field(default=None, description="订单编号")
    serialNumberList: Optional[List[str]] = Field(default=None, description="SN码列表，30位以内字符，当订单API出参orderDeliveryInfo.serialNumberInfo.serialType（商品码类型）值包含[1]时，发货必传SN码")
    imeiList: Optional[List[str]] = Field(default=None, description="IMEI码列表，15-17位数字，当订单API出参orderDeliveryInfo.serialNumberInfo.serialType（商品码类型）值包含[2]时，发货必传IMEI码")


class OpenSellerOrderGoodsLogisticsAppendSchema(BaseModel):
    expressCode: Optional[int] = Field(default=None, description="物流公司编码")
    oid: Optional[int] = Field(default=None, description="订单id，只允许传主品订单id")
    expressNo: Optional[str] = Field(default=None, description="快递单号")


class OpenSellerOrderLogisticsUpdateSchema(BaseModel):
    expressCode: Optional[int] = Field(default=None, description="物流公司编码")
    expressNo: Optional[str] = Field(default=None, description="快递单号")
    logisticsId: Optional[int] = Field(default=None, description="包裹id，支持传入订单详情API出参orderLogisticsInfo. logisticsId（主品订单包裹id）或subOrderInfo. subOrderLogisticsInfo.logisticsId（赠品订单包裹id）")
    orderId: Optional[int] = Field(default=None, description="订单id，只允许传入主品订单id，即获取订单详情API出参orderBaseInfo.oid(订单id)")


class OpenSellerOrderNoteAddSchema(BaseModel):
    orderId: Optional[int] = Field(default=None, description="订单编号")
    staffId: Optional[int] = Field(default=None, description="员工ID")
    note: Optional[str] = Field(default=None, description="备注 字符数<=200")
    flag: Optional[int] = Field(default=None, description="	0：表示不插旗; 1：RED; 2：YELLOW; 3：GREEN; 4：BLUE; 5：PURPLE; 6：GREY;")


class OpenSellerOrderSkuUpdateSchema(BaseModel):
    orderId: Optional[int] = Field(default=None, description="订单编号")
    itemId: Optional[int] = Field(default=None, description="订单商品id")
    oldSkuId: Optional[int] = Field(default=None, description="原商品skuId")
    newSkuId: Optional[int] = Field(default=None, description="新商品skuId")
