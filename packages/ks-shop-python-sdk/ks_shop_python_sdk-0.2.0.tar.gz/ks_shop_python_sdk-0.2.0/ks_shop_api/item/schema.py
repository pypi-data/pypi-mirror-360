# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, List, Union


class SkuCertificatePropParam(BaseModel):
    condition: Optional[str] = Field(default=None, description="成色")
    purchasingChannels: Optional[str] = Field(default=None, description="购买渠道")
    batteryEfficiency: Optional[str] = Field(default=None, description="电池效率")
    mainBoard: Optional[str] = Field(default=None, description="主板维修")
    batteryCondition: Optional[str] = Field(default=None, description="电池情况")
    screenCondition: Optional[str] = Field(default=None, description="屏幕情况")
    shellCollision: Optional[str] = Field(default=None, description="外壳碰撞")
    reportUrl: Optional[str] = Field(default=None, description="质检报告url")
    qualityInspectionNo: Optional[str] = Field(default=None, description="质检编号")
    sn: Optional[str] = Field(default=None, description="SN码")
    shellScratch: Optional[str] = Field(default=None, description="外壳划痕")
    shellPaint: Optional[str] = Field(default=None, description="外壳掉漆")
    deviceSystem: Optional[str] = Field(default=None, description="系统设备")


class OpenApiAutoPassSkuDTO(BaseModel):
    skuId: Optional[int] = Field(default=None, description="sku唯一id")
    skuChangeStock: Optional[int] = Field(default=None, description="要更新的库存")
    skuStockChangeType: Optional[int] = Field(default=None, description="1 增加库存 2 减少库存 3 设置库存 免审编辑只支持 1 和 2")
    skuSalePrice: Optional[int] = Field(default=None, description="Sku 价格，单位为分。1 <= 数值 <=9999999")
    skuMarketPrice: Optional[Union[float, int]] = Field(default=None, description="Sku 市场价，单位为分。1 <= 数值 <=9999999")
    skuNick: Optional[str] = Field(default=None, description="	sku编码，分仓商品必填，SKU编码仅支持中英文、数字以及特殊字符")
    relSkuId: Optional[int] = Field(default=None, description="三方skuId")
    skuCertificatePropValues: Optional[SkuCertificatePropParam] = Field(default=None, description="质检参数")
    gtinCode: Optional[str] = Field(default=None, description="sku条形码")


class OpenApiServicePromise(BaseModel):
    freshRotRefund: Optional[bool] = Field(default=None, description="坏了包退")
    brokenRefund: Optional[bool] = Field(default=None, description="破损包退")
    allergyRefund: Optional[bool] = Field(default=None, description="过敏包退")
    crabRefund: Optional[bool] = Field(default=None, description="蟹无忧")
    weightGuarantee: Optional[bool] = Field(default=None, description="足斤足两")


class OpenApiTimeRange(BaseModel):
    startTime: Optional[int] = Field(default=None, description="开始时间时间戳 时间为00: 00: 00")
    endTime: Optional[int] = Field(default=None, description="结束时间时间戳 时间为 23: 59: 59")

class OpenApiUnavailableTimeRule(BaseModel):
    weeks: Optional[List[int]] = Field(default=None, description="不可用星期 1: 周一、2: 周二、3: 周三、4: 周四、5: 周五、6: 周六、7: 周")
    holidays: Optional[List[int]] = Field(default=None, description="不可用节假日 1: 元旦、2: 春节、3: 清明节、4: 劳动节、5: 端午节、6: 国庆节、7: 中秋节")
    timeRanges: Optional[List[OpenApiTimeRange]] = Field(default=None, description="不可用时间范围，最多三组，单位毫秒，每组时间起止相互互斥")


class CustomerInfo(BaseModel):
    customerInfoType: Optional[str] = Field(default=None, description="1-不需要、2-需要1位出行人、3-需要全部出行人")
    customerCertificateType: Optional[List[str]] = Field(default=None, description="如果出行人信息选择，需要1位出行人、需要全部出行人 选项, 则展示出行人证件，且必传，1-身份证")

class ServiceRule(BaseModel):
    refundRule: Optional[str] = Field(default=None, description="退款规则，请求内容为枚举数值，非后面文案： 1:支持7天无理由退货 4:不支持7天无理由退货 5:支持7天无理由退货(拆封后不支持) 6:支持7天无理由退货(激活后不支持) 7:支持7天无理由退货(安装后不支持) 8:支持7天无理由退货(定制类不支持) 9:支持7天无理由退货(使用后不支持) ，由open.item.category.config获得（退款规则会根据类目变化而变化）")
    deliverGoodsInteralTime: Optional[int] = Field(default=None, description="发货间隔时间，单位：秒，范围在[3,15天] 需要转换为秒 259200 为3天，deliverGoodsInteralTime和promiseDeliveryTime至少填一个且不能都填。填deliverGoodsInteralTime代码预售商品，填promiseDeliveryTime代表非预售商品。（如果需要取消请传 0 或 -1），需要注意具体预售时长会根据具体类目不同")
    promiseDeliveryTime: Optional[int] = Field(default=None, description="非预售商品承诺发货时间，单位：秒，取值86400,172800,分别代表24、48小时，deliverGoodsInteralTime和promiseDeliveryTime至少填一个且不能都填。填deliverGoodsInteralTime代码预售商品，填promiseDeliveryTime代表非预售商品。（如果需要取消请传 0 或 -1）")
    immediatelyOnOfflineFlag: Optional[int] = Field(default=None, description="是否立即上架 ,0立即上架，1不立即上架")
    deliveryMethod: Optional[str] = Field(default=None, description="发货方式 logistics：物流配送（默认） certificate：电子凭证")
    servicePromise: Optional[OpenApiServicePromise] = Field(default=None, description="""服务承诺：freshRotRefund：坏了包退
                                                                                        brokenRefund：破损包退
                                                                                        allergyRefund：过敏包退""")
    unavailableTimeRule: Optional[OpenApiUnavailableTimeRule] = Field(default=None, description="电子凭证不可用时间")
    certMerchantCode: Optional[str] = Field(default=None, description="码商，仅有deliveryMethod 为certificate：电子凭证时，此字段才有值，且需校验 ks：快手平台发码 merchant：商家发码")
    certExpireType: Optional[int] = Field(default=None, description="电子凭证有效期类型，仅有deliveryMethod 为certificate：电子凭证时，此字段才有值 1：日期范围；2：仅有截止日期；3：有效天数")
    certStartTime: Optional[int] = Field(default=None, description="开始时间，仅有deliveryMethod 为certificate：电子凭证时，certExpireType为1或2时此字段才有值")
    certEndTime: Optional[int] = Field(default=None, description="截止时间，仅有deliveryMethod 为certificate：电子凭证时，certExpireType为1或2时此字段才有值")
    certExpDays: Optional[int] = Field(default=None, description="有效天数，仅有deliveryMethod 为certificate：电子凭证时，certExpireType为3时此字段才有值")
    orderPurchaseLimitType: Optional[int] = Field(default=None, description="订单限购类型0：未设置；1:已设置最少购买件数；2:已设置最多购买件数；3:最少最多购买件数均设置")
    minOrderCount: Optional[int] = Field(default=None, description="每笔订单最少购买件数，若orderPurchaseLimitType设置为0，建议此字段同样修改为0")
    maxOrderCount: Optional[int] = Field(default=None, description="每笔订单最多购买件数，若orderPurchaseLimitType设置为0，建议此字段同样修改为0")
    customerInfo: Optional[CustomerInfo] = Field(default=None, description="酒旅类目，且选择“电子凭证”，必填")
    priceProtectDays: Optional[int] = Field(default=None, description="价保天数，不传则覆盖为0")
    deliveryTimeMode: Optional[str] = Field(default=None, description="发货时效模式 spot：全部现货；presale：全部预售；spotPresale：现货+预售。值为spotPresale时，promiseDeliveryTime，deliverGoodsInteralTime字段不可传值")


class OpenItemAutopassEditSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品唯一id")
    purchaseLimit: Optional[bool] = Field(default=None, description="是否限购")
    limitCount: Optional[int] = Field(default=None, description="限购数量")
    itemRemark: Optional[str] = Field(default=None, description="商品备注")
    skuList: Optional[List[OpenApiAutoPassSkuDTO]] = Field(default=None, description="商品sku列表")
    serviceRule: Optional[ServiceRule] = Field(default=None, description="服务规则")
    expressTemplateId: Optional[int] = Field(default=None, description="运费模板Id")
    saleTimeFlag: Optional[bool] = Field(default=None, description="是否定点开售")
    timeOfSale: Optional[int] = Field(default=None, description="定点开售时间")
    payWay: Optional[int] = Field(default=None, description="支付方式：1 货到付款 2 在线支付 3 在线支付和货到付款")


class OpenItemBrandListGetSchema(BaseModel):
    cursor: Optional[int] = Field(default=None, description="cursor第一次请求传0，之后传rpc接口返回的cursor值，最大不能超过2000")
    categoryId: Optional[int] = Field(default=None, description="类目id")
    propId: Optional[int] = Field(default=None, description="从获取类目属性值接口中获取“品牌”的propId")
    propValue: Optional[str] = Field(default=None, description="用作模糊查询关键字")


class OpenItemCategorySchema(BaseModel):
    pass


class OpenItemCategoryConfigSchema(BaseModel):
    categoryId: Optional[int] = Field(default=None, description="类目id")


class OpenItemCategoryOptionalGetSchema(BaseModel):
    pass


class OpenItemCategoryPropStandardGetSchema(BaseModel):
    leafCategoryId: Optional[int] = Field(default=None, description="叶子类目ID")


class OpenItemCategoryPropValueSearchSchema(BaseModel):
    categoryId: Optional[int] = Field(default=None, description="类目id")
    propId: Optional[int] = Field(default=None, description="属性id，必填")
    propValue: Optional[str] = Field(default=None, description="属性值")
    cursor: Optional[int] = Field(default=None, description="游标，如果propId=102,则最大允许输入2000")
    limit: Optional[int] = Field(default=None, description="分页数量，最大500")


class OpenItemCategoryStandardCheckSchema(BaseModel):
    leafCategoryId: Optional[int] = Field(default=None, description="叶子类目ID")


class StandardKeyProp(BaseModel):
    propId: Optional[int] = Field(default=None, description="属性项ID")
    propName: Optional[str] = Field(default=None, description="属性项名称")
    inputType: Optional[str] = Field(default=None, description="输入类型：RADIO：单选")
    propValueId: Optional[int] = Field(default=None, description="属性值ID")
    propValueName: Optional[str] = Field(default=None, description="属性值名称")


class OpenItemCategoryStandardSearchSchema(BaseModel):
    standardId: Optional[int] = Field(default=None, description="标品ID")
    leafCategoryId: Optional[int] = Field(default=None, description="叶子类目ID")
    standardKeyPropList: Optional[List[StandardKeyProp]] = Field(default=None, description="标品属性列表")


class OpenItemCategoryStandardSearchSpuSchema(BaseModel):
    standardId: Optional[int] = Field(default=None, description="标品ID")
    leafCategoryId: Optional[int] = Field(default=None, description="叶子类目ID")
    standardKeyPropList: Optional[List[StandardKeyProp]] = Field(default=None, description="标品属性列表")


class OpenItemCategorySuggestedGetSchema(BaseModel):
    imageUrls: Optional[List[str]] = Field(default=None, description="商品图片信息，至少包含一张图片且仅支持快手图片的URL")
    itemTitle: Optional[str] = Field(default=None, description="商品标题")
    itemDesc: Optional[str] = Field(default=None, description="商品描述")


class OpenItemDeleteSchema(BaseModel):
    kwaiItemId: Optional[int] = Field(default=None, description="快手商品ID")
    relItemId: Optional[int] = Field(default=None, description="外部商品id，仅供记录外部商品和快手商品对应关系")


class OpenItemDeletedGetSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")


class OpenItemDeliveryTimeUpdateSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")
    deliverGoodsInteralTime: Optional[int] = Field(default=None, description="发货间隔时间，单位：秒，范围在[3,15天] 需要转换为秒 259200 为3天，deliverGoodsInteralTime和promiseDeliveryTime至少填一个且不能都填。填deliverGoodsInteralTime代码预售商品，填promiseDeliveryTime代表非预售商品。（如果需要取消请传 0 或 -1），需要注意具体预售时长会根据具体类目不同")
    promiseDeliveryTime: Optional[int] = Field(default=None, description="非预售商品承诺发货时间，单位：秒，取值86400,172800,分别代表24、48小时，deliverGoodsInteralTime和promiseDeliveryTime至少填一个且不能都填。填deliverGoodsInteralTime代码预售商品，填promiseDeliveryTime代表非预售商品。（如果需要取消请传 0 或 -1）")
    deliveryTimeMode: Optional[str] = Field(default=None, description="发货时效模式 spot：全部现货；presale：全部预售")


class OpenItemDetailImagesUpdateSchema(BaseModel):
    kwaiItemId: Optional[int] = Field(default=None, description="快手商品ID")
    detailImageUrls: Optional[List[str]] = Field(default=None, description="""1. 请勿出现其它平台的信息水印查看图示；
                                                                                2. 最多上传20张图片；
                                                                                3. 单张图片大小不超过2M，支持png/jpeg/webp/bmp格式；

                                                                                注意：会把传过来的图片信息更新到数据库，不填就相当于删除所有图片""")


class ItemProductClientInfo(BaseModel):
    appType: Optional[str] = Field(default=None, description="app类型")
    clientId: Optional[int] = Field(default=None, description="客户端类型 1 IOS 2 安卓")
    appVer: Optional[str] = Field(default=None, description="app版本")


class OpenItemDetailPageLinkSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")
    type: Optional[int] = Field(default=None, description="跳转类型，1：直接跳商详页 2：跳进直播间打开商详页")
    itemProductClientInfo: Optional[ItemProductClientInfo] = Field(default=None, description="客户端信息")


class OpenItemDiagnosisGetSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")


class OpenapiSkuPropMeasureValueProto(BaseModel):
    type: Optional[str] = Field(default=None, description="""度量衡组件类型："PREVIEW_TEXT" 固定文本组件类型；"TEXT" 文本输入组件类型；"OPERATOR" 符号组件类型""")
    value: Optional[str] = Field(default=None, description="度量衡组件值")
    unitValueId: Optional[int] = Field(default=None, description="单位ID")
    unitValueName: Optional[str] = Field(default=None, description="单位名称")


class OpenapiSkuPropMeasureProto(BaseModel):
    templateId: Optional[int] = Field(default=None, description="度量衡模版ID")
    value: Optional[List[OpenapiSkuPropMeasureValueProto]] = Field(default=None, description="度量衡组件值")


class OpenApiAddSkuPropDTO(BaseModel):
    propName: Optional[str] = Field(default=None, description="规格名称")
    propValueName: Optional[str] = Field(default=None, description="规格值名称")
    imageUrl: Optional[str] = Field(default=None, description="1、图片url, 如果是主属性图片必传。2、0 < 长度 <= 2000，图片大小不超过2M。3、支持png/jpeg/jpg格式。4、必须是快手平台图片url（外网图片链接可通过 open.item.image.upload 提前转换）")
    isMainProp: Optional[int] = Field(default=None, description="1是 0 否 ，是否是主属性，主属性标记为关联sku规格图片")
    propValueGroupId: Optional[int] = Field(default=None, description="规格值分组id")
    propVersion: Optional[int] = Field(default=None, description="销售属性版本 自定义1，使用类目模板传2")
    propSortNum: Optional[int] = Field(default=None, description="【属性排序值】升序排列，如颜色、尺码两种规格，颜色规格为1，尺码规格为2，则颜色在前尺码在后")
    propValueSortNum: Optional[int] = Field(default=None, description="【属性值排序值】升序排列，如红色、黑色两种规格值，红色为1，黑色为2，则红色在前黑色在后")
    propValueRemarks: Optional[str] = Field(default=None, description="规格备注")
    measureInfo: Optional[OpenapiSkuPropMeasureProto] = Field(default=None, description="规格对应的度量衡信息")


class MealContentDTO(BaseModel):
    title: Optional[str] = Field(default=None, description="内容项标题（20字符以内）")
    count: Optional[int] = Field(default=None, description="内容项数量（输入数字不超过4位）")
    price: Optional[int] = Field(default=None, description="内容项单价（单位分），最大值9999900")


class MealGroupDTO(BaseModel):
    title: Optional[str] = Field(default=None, description="套餐分组名称（限制10个字符）")
    mealContentDTOList: Optional[List[MealContentDTO]] = Field(default=None, description="套餐内容列表，最多10个内容项，内容项数量不超过4位数字，单价单位分，最大值9999900")
    fromNum: Optional[int] = Field(default=None, description="套餐内容项 几选几（第一个几），最小值1，最大值套餐分组数量")
    selectNum: Optional[int] = Field(default=None, description="套餐内容项 几选几（第二个几），最小值1，最大值套餐分组数量")


class MealDetailDTO(BaseModel):
    mealGroupDTOList: Optional[List[MealGroupDTO]] = Field(default=None, description="套餐分组，最多定义10个分组")
    lowestPeopleNum: Optional[int] = Field(default=None, description="最低用餐人数，最小值1，非必填")
    highestPeopleNum: Optional[int] = Field(default=None, description="最高用餐人数，最大值20，非必填")
    remark: Optional[str] = Field(default=None, description="备注，非必填，最多2000字符")


class OpenApiUpdateSkuDTO(BaseModel):
    skuId: Optional[int] = Field(default=None, description="商品sku唯一id")
    relSkuId: Optional[int] = Field(default=None, description="三方商品skuId")
    skuSalePrice: Optional[int] = Field(default=None, description="Sku 价格，单位为分。1 <= 数值 <=类目配置价格上限")
    skuNick: Optional[str] = Field(default=None, description="sku编码,分仓商品不能为空，SKU编码仅支持中英文、数字以及特殊字符")
    skuProps: Optional[List[OpenApiAddSkuPropDTO]] = Field(default=None, description="商品规格多属性规格参数。目前支持三级属性，并且需要传三级属性的完整笛卡尔积。录入多规格商品时，需要包含所有规格的组合")
    skuCertificate: Optional[SkuCertificatePropParam] = Field(default=None, description="质检参数")
    skuStockChangeType: Optional[int] = Field(default=None, description="1 增加库存 2 减少库存 3 设置库存 免审编辑只支持 1 和 2")
    skuChangeStock: Optional[int] = Field(default=None, description="变更的库存数量")
    skuMarketPrice: Optional[Union[float, int]] = Field(default=None, description="""商品划线价
                                                                                        注意：划线价必须大于当前商品的最高单价，并且
                                                                                        划线价不可超过单价的10倍""")
    gtinCode: Optional[str] = Field(default=None, description="	sku条形码")
    mealDetail: Optional[MealDetailDTO] = Field(default=None, description="套餐详情，商品类型为团购时，才可使用该字段，非必传")


class CategoryPropValueParam(BaseModel):
    propValueId: Optional[int] = Field(default=None, description="属性值id")
    propValue: Optional[str] = Field(default=None, description="属性值")


class DateRangeParam(BaseModel):
    startTimeTimestamp: Optional[int] = Field(default=None, description="起始时间（毫秒）")
    endTimeTimestamp: Optional[int] = Field(default=None, description="结束时间（毫秒）")


class ItemPropValue(BaseModel):
    propId: Optional[int] = Field(default=None, description="属性id（规格数量上限200，规格值数量上限500）")
    radioPropValue: Optional[CategoryPropValueParam] = Field(default=None, description="单选属性 (根据open.item.category.config中propInputType和required判断是否必填)")
    checkBoxPropValuesList: Optional[List[CategoryPropValueParam]] = Field(default=None, description="多选属性 (根据open.item.category.config中propInputType和required判断是否必填)")
    textPropValue: Optional[str] = Field(default=None, description="文本属性值 (根据open.item.category.config中propInputType和required判断是否必填，不允许传空字符串)")
    datetimeTimestamp: Optional[int] = Field(default=None, description="时间戳属性 (根据open.item.category.config中propInputType和required判断是否必填)")
    dateRange: Optional[DateRangeParam] = Field(default=None, description="时间范围属性 (根据open.item.category.config中propInputType和required判断是否必填)")
    sortNum: Optional[int] = Field(default=None, description="序号，open.item.category.config返回")
    imagePropValues: Optional[List[str]] = Field(default=None, description="图片属性列表 (根据open.item.category.config中propInputType和required判断是否必填)")
    propName: Optional[str] = Field(default=None, description="属性名称")
    propAlias: Optional[str] = Field(default=None, description="属性别名")
    inputType: Optional[int] = Field(default=None, description="1-文本 2-checkbox 3-数字 4-邮箱 5-日期 6-url地址 7-时间范围 8-单选框 9-图片")
    propType: Optional[int] = Field(default=None, description="1-sku属性 2-商品属性")
    unitPropValueId: Optional[int] = Field(default=None, description="单位属性值Id，open.item.category.config返回")
    unitPropValueName: Optional[str] = Field(default=None, description="单位属性值名称")


class AddItemPropValue(BaseModel):
    propId: Optional[int] = Field(default=None, description="属性id（规格数量上限200，规格值数量上限500）")
    radioPropValue: Optional[CategoryPropValueParam] = Field(default=None, description="单选属性 (根据open.item.category.config中propInputType和required判断是否必填)")
    checkBoxPropValuesList: Optional[List[CategoryPropValueParam]] = Field(default=None, description="多选属性 (根据open.item.category.config中propInputType和required判断是否必填)")
    textPropValue: Optional[str] = Field(default=None, description="文本属性值 (根据open.item.category.config中propInputType和required判断是否必填，不允许传空字符串)")
    datetimeTimestamp: Optional[int] = Field(default=None, description="时间戳属性 (根据open.item.category.config中propInputType和required判断是否必填)")
    dateRange: Optional[DateRangeParam] = Field(default=None, description="时间范围属性 (根据open.item.category.config中propInputType和required判断是否必填)")
    sortNum: Optional[int] = Field(default=None, description="序号，open.item.category.config返回")
    imagePropValues: Optional[List[str]] = Field(default=None, description="图片属性列表 (根据open.item.category.config中propInputType和required判断是否必填)")
    propName: Optional[str] = Field(default=None, description="属性名称")
    propAlias: Optional[str] = Field(default=None, description="属性别名")
    inputType: Optional[int] = Field(default=None, description="1-文本 2-checkbox 3-数字 4-邮箱 5-日期 6-url地址 7-时间范围 8-单选框 9-图片")
    propType: Optional[int] = Field(default=None, description="1-sku属性 2-商品属性")
    unitPropValueId: Optional[int] = Field(default=None, description="单位属性值Id，open.item.category.config返回")
    unitPropValueName: Optional[str] = Field(default=None, description="单位属性值名称")


class QualificationDataDTO(BaseModel):
    metaId: Optional[int] = Field(default=None, description="资质元id")
    existedQualificationDataId: Optional[int] = Field(default=None, description="已有的资质数据id")
    prop: Optional[AddItemPropValue] = Field(default=None, description="资质元属性值")


class ItemVideoProto(BaseModel):
    videoId: Optional[str] = Field(default=None, description="视频 ID")
    videoType: Optional[int] = Field(default=None, description="视频类型，1-本地上传视频 2-快手短视频。")


class OpenItemEditSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")
    title: Optional[str] = Field(default=None, description="商品名称")
    categoryId: Optional[int] = Field(default=None, description="类目ID")
    imageUrls: Optional[List[str]] = Field(default=None, description="""商品主图，1. 最多上传9张图片
                                                                                2. 单张图片大小不超过2M，支持png/jpeg/jpg格式
                                                                                3.必须是快手平台图片url（外网图片链接可通过 open.item.image.upload 提前转换）""")
    skuList: Optional[List[OpenApiUpdateSkuDTO]] = Field(default=None, description="sku信息列表。0 < 数量 <= 600")
    itemVideoId: Optional[str] = Field(default=None, description="商品关联的短视频id")
    purchaseLimit: Optional[bool] = Field(default=None, description="商品是否限购；true:限购，false:不限购")
    limitCount: Optional[int] = Field(default=None, description="商品限购数量，当purchaseLimit为true时，必填")
    itemPropValues: Optional[List[ItemPropValue]] = Field(default=None, description="商品类目属性，商品类目属性有必填项，必传。（注意：商品类目属性不允许重复）")
    details: Optional[str] = Field(default=None, description="商品详情描述。0 < 长度 <= 1000个汉字(2000个字符)")
    detailImageUrls: Optional[List[str]] = Field(default=None, description="""商品详情图，1. 单张图片大小不超过2M，支持png/jpeg/jpg格式；2. 必须为快手图片链接（外网图片链接可通过 open.item.image.upload 提前转换）""")
    updateDetailImageUrls: Optional[bool] = Field(default=None, description="是否更新商品详情图，detailImageUrls传[]，并且updateItemPropValues 传true 会清空商品详情图，（如果需要改商品详情图的话需要传true）")
    itemRemark: Optional[str] = Field(default=None, description="支持中文、英文和数字，最多10个汉字(20个字符）")
    serviceRule: Optional[ServiceRule] = Field(default=None, description="服务规则")
    expressTemplateId: Optional[int] = Field(default=None, description="运费模板id")
    saleTimeFlag: Optional[bool] = Field(default=None, description="是否定点开售，true为定点开售，false为正常售卖")
    timeOfSale: Optional[int] = Field(default=None, description="定点开售时间，如果saleTimeFlag为true时此项必填")
    payWay: Optional[int] = Field(default=None, description="支付方式：1 货到付款 2 在线支付 3 在线支付和货到付款；默认2 目前OpenAPI端只支持「在线支付」方式")
    updateItemPropValues: Optional[bool] = Field(default=None, description="是否更新商品类目属性，itemPropValues传[]，并且updateItemPropValues 传true 会清空商品类目属性，如果商品类目属性有必填项会更新失败（如果需要改类目属性的话需要传true）")
    poiIds: Optional[List[int]] = Field(default=None, description="门店ID")
    whiteBaseImageUrl: Optional[str] = Field(default=None, description="商品白底图，请上传格式为png/jpeg/jpg的图片，长宽比为1:1的图片，像素480*480px以上的图片，大小小于2M")
    transparentImageUrl: Optional[str] = Field(default=None, description="商品透明图，请上传格式为png的图片，长宽比为1:1的图片，像素480*480px以上的图片，大小小于2M")
    shortTitle: Optional[str] = Field(default=None, description="商品短标题长度必须大于4且小于20个字符（2-10汉字）")
    sellingPoint: Optional[str] = Field(default=None, description="商品卖点长度必须大于8且小于24个字符（4-12汉字）")
    instructions: Optional[str] = Field(default=None, description="使用说明，非必传，约定字符限制400个中文字长度以内。空行数量10行以内。")
    saveShelfItemQualificationData: Optional[List[QualificationDataDTO]] = Field(default=None, description="商品资质")
    updateItemQualification: Optional[bool] = Field(default=None, description="是否更新商品资质信息")
    spuId: Optional[int] = Field(default=None, description="标品ID，标品强管控类目必填，标品弱管控类目非必填，标品不管控或未配置类目不允许填写")
    updateThreeQuartersImageUrls: Optional[bool] = Field(default=None, description="是否更新3:4主图")
    threeQuartersImageUrls: Optional[List[str]] = Field(default=None, description="3:4主图")
    itemVideo: Optional[ItemVideoProto] = Field(default=None, description="商品视频商品视频（优先从 itemVideoId 字段取快手短视频 ID，再从当前字段取视频信息）")


class OpenItemGetSchema(BaseModel):
    kwaiItemId: Optional[int] = Field(default=None, description="商品ID")


class OpenItemImageUploadSchema(BaseModel):
    imgUrl: Optional[str] = Field(default=None, description="图片原始url")
    imgBytes: Optional[bytes] = Field(default=None, description="Content-Type必须使用multipart/form-data;charset=utf-8传入数据，此字段为参数顶层，按照图片字节数组（不是base64）方式传入。可以点击上传商品图片接口请求示例查看")
    uploadType: Optional[str] = Field(default=None, description="1（商品主图）、 2（商品详情图）、 3（sku图片）、 4（类目属性图片）、 5（商品白底图，请上传格式为png/jpeg/jpg的图片，长宽比为1: 1的图片，像素480*480px以上的图片，大小小于2M）、 6（商品透明图，请上传格式为png的图片，长宽比为1: 1的图片，像素480*480px以上的图片，大小小于2M）、 9（标品图片）")


class OpenItemListGetSchema(BaseModel):
    kwaiItemId: Optional[int] = Field(default=None, description="快手商品ID")
    relItemId: Optional[int] = Field(default=None, description="外部商品Id.如kwaiItemId未传，但relItemId传了，将会按照appkey+relItemId查询")
    itemStatus: Optional[int] = Field(default=None, description="商品状态。不传kwaiItemId和relItemId时才会生效 1-正常 目前接口只支持1-正常（商品状态1是指未删除的商品）")
    itemType: Optional[int] = Field(default=None, description="商品类型。不传kwaiItemId和relItemId时才会生效 1-自建商品")
    pageNumber: Optional[int] = Field(default=None, description="0 < 数值 < totalPage")
    pageSize: Optional[int] = Field(default=None, description="推荐值20，范围为10～100，超过100或不传默认取100")
    onOfflineStatus: Optional[int] = Field(default=None, description="上下架条件，目前仅支持查询1（上架）商品")


class OpenItemMainPicVideoApplySchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")
    videoId: Optional[str] = Field(default=None, description="视频ID")
    videoType: Optional[int] = Field(default=None, description="视频类型，1-本地上传视频 2-快手短视频。")


class OpenItemMainPicVideoDeleteSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")


class OpenItemMaterialDetailGetSchema(BaseModel):
    materialId: Optional[int] = Field(default=None, description="素材ID")
    materialUploadType: Optional[int] = Field(default=None, description="商品素材上传类型：1 商品视频")


class OpenItemMaterialUploadTokenIssueSchema(BaseModel):
    materialUploadType: Optional[int] = Field(default=None, description="商品素材上传类型：1 商品视频")
    fileName: Optional[str] = Field(default=None, description="""素材文件名。非必传，如果不传系统将自动根据当前时间生成文件名，如"20250527114242.mp4"。""")
    fileLength: Optional[int] = Field(default=None, description="素材文件大小（单位字节）。非必传，用于系统校验素材大小。如果传入，系统在签发上传令牌时即可快速校验大小非法的素材。如果不传，系统将在完成素材上传时校验视频大小。")


class OpenItemMaterialUploadTokenVerifySchema(BaseModel):
    token: Optional[str] = Field(default=None, description="上传令牌")
    materialUploadType: Optional[int] = Field(default=None, description="商品素材上传类型：1 商品视频")


class OpenApiAddSkuDTO(BaseModel):
    relSkuId: Optional[int] = Field(default=None, description="三方skuId")
    skuStock: Optional[int] = Field(default=None, description="	Sku 库存。0 <= 数值 <= 9999999")
    skuSalePrice: Optional[int] = Field(default=None, description="Sku 价格，单位为分。1 <= 数值 <=类目配置价格上限")
    skuNick: Optional[str] = Field(default=None, description="sku编码,分仓商品不能为空，SKU编码仅支持中英文、数字以及特殊字符")
    skuProps: Optional[List[OpenApiAddSkuPropDTO]] = Field(default=None, description="商品规格多属性规格参数。目前支持三级属性，并且需要传三级属性的完整笛卡尔积。录入多规格商品时，需要包含所有规格的组合")
    skuCertificate: Optional[SkuCertificatePropParam] = Field(default=None, description="质检参数，二手类型商品需要添加")
    skuMarketPrice: Optional[Union[float, int]] = Field(default=None, description="""商品划线价
                                                                                        注意：划线价必须大于当前商品的最高单价，并且
                                                                                        划线价不可超过单价的10倍""")
    goodsId: Optional[str] = Field(default=None, description="货品Id，多仓商品支持字段")
    gtinCode: Optional[str] = Field(default=None, description="	sku条形码")
    mealDetail: Optional[MealDetailDTO] = Field(default=None, description="套餐详情，商品类型为团购时，才可使用该字段，非必传")


class OpenItemNewSchema(BaseModel):
    title: Optional[str] = Field(default=None, description="商品名称")
    relItemId: Optional[int] = Field(default=None, description="外部商品id，仅供记录外部商品和快手商品对应关系； 注意：外部商品id不可与历史新建商品重复")
    categoryId: Optional[int] = Field(default=None, description="类目ID")
    imageUrls: Optional[List[str]] = Field(default=None, description="""商品主图，1. 最多上传9张图片
                                                                                2. 单张图片大小不超过2M，支持png/jpeg/jpg格式
                                                                                3.必须是快手平台图片url（外网图片链接可通过 open.item.image.upload 提前转换）""")
    skuList: Optional[List[OpenApiAddSkuDTO]] = Field(default=None, description="sku信息列表。0 < 数量 <= 600")
    purchaseLimit: Optional[bool] = Field(default=None, description="是否限购，默认不限购")
    limitCount: Optional[int] = Field(default=None, description="限购数量，当purchaseLimit为true时，必填")
    itemPropValues: Optional[List[AddItemPropValue]] = Field(default=None, description="商品类目属性，商品类目属性有必填项，必传。（注意：商品类目属性不允许重复）")
    details: Optional[str] = Field(default=None, description="商品详情描述。0 < 长度 <= 1000个汉字(2000个字符)")
    detailImageUrls: Optional[List[str]] = Field(default=None, description="""商品详情图，1. 至少上传 1 张；2. 最多上传50张；3. 单张图片大小不超过2M，支持png/jpeg/jpg格式；4. 必须为快手图片链接（外网图片链接可通过 open.item.image.upload 提前转换）""")
    stockPartner: Optional[bool] = Field(default=None, description="是否分仓，默认为false")
    itemRemark: Optional[str] = Field(default=None, description="支持中文、英文和数字，最多10个汉字(20个字符）")
    serviceRule: Optional[ServiceRule] = Field(default=None, description="服务规则")
    expressTemplateId: Optional[int] = Field(default=None, description="运费模板id")
    saleTimeFlag: Optional[bool] = Field(default=None, description="是否定点开售，默认为false")
    timeOfSale: Optional[int] = Field(default=None, description="定点开售时间，如果开启定点开售必填")
    payWay: Optional[int] = Field(default=None, description="支付方式：1 货到付款 2 在线支付 3 在线支付和货到付款；默认2 目前OpenAPI端只支持「在线支付」方式")
    multipleStock: Optional[bool] = Field(default=None, description="是否是多仓库存模式，默认是false")
    poiIds: Optional[List[int]] = Field(default=None, description="门店ID")
    whiteBaseImageUrl: Optional[str] = Field(default=None, description="商品白底图，请上传格式为png/jpeg/jpg的图片，长宽比为1:1的图片，像素480*480px以上的图片，大小小于2M")
    transparentImageUrl: Optional[str] = Field(default=None, description="商品透明图，请上传格式为png的图片，长宽比为1:1的图片，像素480*480px以上的图片，大小小于2M")
    shortTitle: Optional[str] = Field(default=None, description="商品短标题长度必须大于4且小于20个字符（2-10汉字）")
    sellingPoint: Optional[str] = Field(default=None, description="商品卖点长度必须大于8且小于24个字符（4-12汉字）")
    instructions: Optional[str] = Field(default=None, description="使用说明，非必传，约定字符限制400个中文字长度以内。空行数量10行以内。")
    saveShelfItemQualificationData: Optional[List[QualificationDataDTO]] = Field(default=None, description="商品资质")
    offShoreMode: Optional[int] = Field(default=None, description="离岛模式（目前仅支持离岛补购）；1:离岛补购；2:离岛免税")
    spuId: Optional[int] = Field(default=None, description="标品ID，标品强管控类目必填，标品弱管控类目非必填，标品不管控或未配置类目不允许填写")
    itemVideoId: Optional[str] = Field(default=None, description="短视频ID")
    threeQuartersImageUrls: Optional[List[str]] = Field(default=None, description="3:4主图")
    itemVideo: Optional[ItemVideoProto] = Field(default=None, description="商品视频商品视频（优先从 itemVideoId 字段取快手短视频 ID，再从当前字段取视频信息）")


class OpenItemNewPrecheckSchema(BaseModel):
    leafCategoryId: Optional[int] = Field(default=None, description="商品叶子类目id（非必填，不传则不校验类目相关规则）")


class PropValueOpenApiDTO(BaseModel):
    propValueId: Optional[int] = Field(default=None, description="属性值ID")
    propValue: Optional[str] = Field(default=None, description="属性值名称")


class KeyPropOpenApiDTO(BaseModel):
    propName: Optional[str] = Field(default=None, description="属性名")
    unitPropValueId: Optional[int] = Field(default=None, description="单位值ID")
    propId: Optional[int] = Field(default=None, description="属性ID")
    propValue: Optional[PropValueOpenApiDTO] = Field(default=None, description="属性值")
    templatePropType: Optional[int] = Field(default=None, description="属性模版类型")
    sortNum: Optional[int] = Field(default=None, description="排序值")
    unitPropValueName: Optional[str] = Field(default=None, description="单位值名称")
    inputType: Optional[str] = Field(default=None, description="输入类型")
    propAlias: Optional[str] = Field(default=None, description="属性别名")
    propType: Optional[str] = Field(default=None, description="属性类型")
    propDesc: Optional[str] = Field(default=None, description="属性描述")


class SPUPropOpenApiDTO(BaseModel):
    unitPropValueId: Optional[int] = Field(default=None, description="属性值ID")
    radioPropValue: Optional[PropValueOpenApiDTO] = Field(default=None, description="单选属性")
    propId: Optional[int] = Field(default=None, description="属性ID")
    inputType: Optional[str] = Field(default=None, description="输入类型")
    propAlias: Optional[str] = Field(default=None, description="属性别名")
    propType: Optional[str] = Field(default=None, description="属性类型")
    propName: Optional[str] = Field(default=None, description="属性名称")
    textPropValue: Optional[str] = Field(default=None, description="文本属性值")
    checkboxPropValue: Optional[List[PropValueOpenApiDTO]] = Field(default=None, description="多选属性值")
    templatePropType: Optional[int] = Field(default=None, description="属性模版类型")
    sortNum: Optional[int] = Field(default=None, description="排序值")
    unitPropValueName: Optional[str] = Field(default=None, description="属性值名")
    propDesc: Optional[str] = Field(default=None, description="属性描述")


class OpenItemOpenItemStandardCorrectSpuSchema(BaseModel):
    standardId: Optional[int] = Field(default=None, description="标品ID")
    keyPropDto: Optional[List[KeyPropOpenApiDTO]] = Field(default=None, description="关键属性")
    modifyReason: Optional[str] = Field(default=None, description="纠错原因")
    standardImage: Optional[List[str]] = Field(default=None, description="标品图片：最多上传上传9张，有的标品不支持标品图片上传，这个需要根据查询标品模版确认 注意：标品图片必须是快手图片！")
    standardOtherImages: Optional[str] = Field(default=None, description="其他图片")
    modifyImageUrl: Optional[str] = Field(default=None, description="纠错图片（注意：标品图片必须是快手图片！）")
    operatorSource: Optional[int] = Field(default=None, description="操作源")
    categoryId: Optional[int] = Field(default=None, description="类目ID")
    userId: Optional[int] = Field(default=None, description="用户ID")
    spuPropDto: Optional[List[SPUPropOpenApiDTO]] = Field(default=None, description="spu属性")
    standardApplyId: Optional[int] = Field(default=None, description="标品申报ID")
    standardName: Optional[str] = Field(default=None, description="标品名")
    bizIdentityCode: Optional[str] = Field(default=None, description="业务身份编码")
    rootBizIdentityCode: Optional[str] = Field(default=None, description="根业务身份编码")
    applyType: Optional[int] = Field(default=None, description="申请类型")


class OpenItemQualificationCollectionConfigSchema(BaseModel):
    categoryId: Optional[int] = Field(default=None, description="叶子类目ID")


class OpenItemSalepropRuleSchema(BaseModel):
    categoryId: Optional[int] = Field(default=None, description="类目ID")
    spuId: Optional[int] = Field(default=None, description="如果是标品发品流程，需要传入标品id")
    itemId: Optional[int] = Field(default=None, description="商品id，新发时传0")


class OpenItemShelfStatusUpdateSchema(BaseModel):
    kwaiItemId: Optional[int] = Field(default=None, description="快手商品ID")
    shelfStatus: Optional[int] = Field(default=None, description="商品上架状态。0:下架； 1:上架。")


class SkuGoodsRelationParam(BaseModel):
    goodsId: Optional[str] = Field(default=None, description="货品ID")
    skuId: Optional[int] = Field(default=None, description="商品sku唯一id")


class OpenItemSkuGoodsRelationAddSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")
    skuGoodsRelation: Optional[List[SkuGoodsRelationParam]] = Field(default=None, description="sku与货品关联信息")


class OpenItemSkuGoodsRelationDeleteSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")
    skuGoodsRelation: Optional[List[SkuGoodsRelationParam]] = Field(default=None, description="sku与货品关联信息")
    updateItemStockModel: Optional[bool] = Field(default=None, description="是否将库存模式切换到商品库存模式")


class OpenItemSkuGoodsRelationGetSchema(BaseModel):
    skuId: Optional[int] = Field(default=None, description="商品sku唯一id")


class OpenItemSkuGoodsRelationUpdateSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")
    skuGoodsRelation: Optional[List[SkuGoodsRelationParam]] = Field(default=None, description="sku与货品关联信息")


class OpenItemSkuListGetSchema(BaseModel):
    kwaiItemId: Optional[int] = Field(default=None, description="快手商品ID")
    relSkuId: Optional[int] = Field(default=None, description="外部sku id")
    skuStatus: Optional[int] = Field(default=None, description="状态，1，正常(仅支持状态1)")


class OpenItemSkuPriceUpdateSchema(BaseModel):
    itemId: Optional[int] = Field(default=None, description="商品ID")
    price: Optional[Union[int, float]] = Field(default=None, description="价格")
    skuId: Optional[int] = Field(default=None, description="商品sku唯一id")


class OpenItemSkuStockUpdateSchema(BaseModel):
    kwaiItemId: Optional[int] = Field(default=None, description="快手商品ID")
    skuId: Optional[int] = Field(default=None, description="商品sku唯一id")
    skuChangeStock: Optional[int] = Field(default=None, description="库存变更数量（取值范围：大于 0 小于 9999999，且当前库存+ skuChangeStock 不能大于 9999999）")
    changeType: Optional[int] = Field(default=None, description="变更类型，1-增加 2-减少")


class OpenItemStandardApplySchema(BaseModel):
    keyPropList: Optional[List[KeyPropOpenApiDTO]] = Field(default=None, description="关键属性信息")
    categoryId: Optional[int] = Field(default=None, description="叶子类目ID（类目ID必填）")
    spuPropList: Optional[List[SPUPropOpenApiDTO]] = Field(default=None, description="SPU属性信息")
    standardImages: Optional[List[str]] = Field(default=None, description="标品图片：最多上传上传9张，有的标品不支持标品图片上传，这个需要根据查询标品模版确认 注意：标品图片必须是快手图片！")


class OpenItemProductStandardApplySearchSchema(BaseModel):
    categoryId: Optional[List[int]] = Field(default=None, description="叶子类目id列表")
    standardStatus: Optional[int] = Field(default=None, description="标品状态(-1: 全部，1: 启用，2: 禁用)")
    standardName: Optional[str] = Field(default=None, description="标品名称")
    applyType: Optional[int] = Field(default=None, description="申报类型（-1: 全部，1: 申报记录，2: 纠错记录）")
    standardAuditStatus: Optional[int] = Field(default=None, description="标品审核状态（-1: 全部，1: 审核中，2: 审核通过，3: 审核驳回）")
    limit: Optional[int] = Field(default=None, description="分页使用，一页数据量")
    cursor: Optional[int] = Field(default=None, description="分页使用，开始位置")


class OpenItemStandardApplyQuerySpuSchema(BaseModel):
    cursor: Optional[int] = Field(default=None, description="分页查询使用")
    categoryId: Optional[List[int]] = Field(default=None, description="叶子类目ID列表")
    userId: Optional[int] = Field(default=None, description="商家id")
    standardStatus: Optional[int] = Field(default=None, description="标品状态(-1: 全部，1: 启用，2: 禁用)")
    standardAuditStatus: Optional[int] = Field(default=None, description="标品审核状态（-1: 全部，1: 审核中，2: 审核通过，3: 审核驳回）")
    limit: Optional[int] = Field(default=None, description="分页使用，一页数据量")
    standardName: Optional[str] = Field(default=None, description="标品名称")
    applyType: Optional[int] = Field(default=None, description="申报类型（-1: 全部，1: 申报记录，2: 纠错记录）")


class OpenItemStandardApplySpuSchema(BaseModel):
    keyPropDto: Optional[List[KeyPropOpenApiDTO]] = Field(default=None, description="关键属性")
    categoryId: Optional[int] = Field(default=None, description="类目ID")
    spuPropDto: Optional[List[SPUPropOpenApiDTO]] = Field(default=None, description="spu属性")
    standardImage: Optional[List[str]] = Field(default=None, description="标品图片：最多上传上传9张，有的标品不支持标品图片上传，这个需要根据查询标品模版确认 注意：标品图片必须是快手图片！")
    standardOtherImages: Optional[str] = Field(default=None, description="其他图片 注意：图片必须是快手图片！")


class OpenItemStandardCorrectSchema(BaseModel):
    keyPropList: Optional[List[KeyPropOpenApiDTO]] = Field(default=None, description="关键属性信息")
    categoryId: Optional[int] = Field(default=None, description="类目ID 必填")
    spuPropList: Optional[List[SPUPropOpenApiDTO]] = Field(default=None, description="SPU属性信息")
    standardId: Optional[int] = Field(default=None, description="要纠错的标品ID 必填")
    modifyReason: Optional[str] = Field(default=None, description="纠错原因")
    modifyImageUrl: Optional[str] = Field(default=None, description="纠错图片（注意：标品图片必须是快手图片！）")
    standardImages: Optional[List[str]] = Field(default=None, description="标品图片：最多上传上传9张，有的标品不支持标品图片上传，这个需要根据查询标品模版确认 注意：标品图片必须是快手图片！")


class OpenItemVideoCaptionEditSchema(BaseModel):
    videoId: Optional[str] = Field(default=None, description="视频ID")
    videoType: Optional[int] = Field(default=None, description="视频类型，1-本地上传视频 2-快手短视频。只在 videoType=1时传入有效。")
    caption: Optional[str] = Field(default=None, description="视频标题")


class OpenItemVideoCountSchema(BaseModel):
    videoType: Optional[int] = Field(default=None, description="视频类型，1-本地上传视频 2-快手短视频。")
    aspectRatio: Optional[int] = Field(default=None, description="视频比例，只在 videoType=1时传入有效。0-全部 1-1:1比例 2-4:3比例 3-9:16比例 4-16:9比例 6-4:3比例")
    auditStatus: Optional[int] = Field(default=None, description="审核状态，只在 videoType=1时传入有效。0-全部 1-审核中 2-审核通过 3-审核拒绝；")
    createTimeStart: Optional[int] = Field(default=None, description="视频上传时间范围（起始时间戳）")
    createTimeEnd: Optional[int] = Field(default=None, description="视频上传时间范围（结束时间戳）")


class OpenItemVideoDeleteSchema(BaseModel):
    videoType: Optional[int] = Field(default=None, description="视频类型，1-本地上传视频 2-快手短视频。只在 videoType=1时传入有效。")
    videoId: Optional[List[str]] = Field(default=None, description="视频 ID")


class OpenItemVideoInfoSchema(BaseModel):
    videoId: Optional[str] = Field(default=None, description="视频 ID")
    videoType: Optional[int] = Field(default=None, description="视频类型，1-本地上传视频 2-快手短视频")


class OpenItemVideoListSchema(BaseModel):
    videoType: Optional[int] = Field(default=None, description="视频类型，1-本地上传视频 2-快手短视频。")
    aspectRatio: Optional[int] = Field(default=None, description="视频比例，只在 videoType=1时传入有效。0-全部 1-1:1比例 2-4:3比例 3-9:16比例 4-16:9比例 6-4:3比例")
    auditStatus: Optional[int] = Field(default=None, description="审核状态，只在 videoType=1时传入有效。0-全部 1-审核中 2-审核通过 3-审核拒绝；")
    createTimeStart: Optional[int] = Field(default=None, description="视频上传时间范围（起始时间戳）")
    createTimeEnd: Optional[int] = Field(default=None, description="视频上传时间范围（结束时间戳）")
    pageIndex: Optional[int] = Field(default=None, description="查询页号")
    pageSize: Optional[int] = Field(default=None, description="一页查询数量（最多 50）")
