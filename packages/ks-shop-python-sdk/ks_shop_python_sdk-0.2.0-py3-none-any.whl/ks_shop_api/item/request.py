# -*- coding: utf-8 -*-
import deprecation
from ks_shop_api.base import RestApi
"""
商品API
"""


class OpenItemAutopassEditRequest(RestApi):
    """
    免审编辑商品
    更新时间: 2025-06-20 16:42:43
    更改商品的库存、价格和服务承诺等信息，无需审核直接生效

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.autopass.edit&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.autopass.edit"


class OpenItemBrandListGetRequest(RestApi):
    """
    更新时间: 2025-06-20 17:04:35
    1.获取商品类目下的品牌列表，可以根据品牌名称进行模糊搜索，返回内容有序
    2.若在类目下搜索不到品牌，请检查在该类目下是否进行了品牌申报
    3.商家品牌申报入口-品牌申报(https://s.kwaixiaodian.com/goods/brand/apply?from=edit)
    4.品牌申报查询入口-申报查询(https://s.kwaixiaodian.com/goods/brand/list)

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.brand.list.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.brand.list.get"


class OpenItemCategoryRequest(RestApi):
    """
    获取商品类目列表
    更新时间: 2025-06-20 16:39:22
    1.小店商品类目的变更频率较低，无需频繁拉取
    2.请关注快手小店类目更新动态，按需重新拉取更新，类目更新动态请关注《快手小店开放类目及资质一览表》(https://www.kwaixiaodian.com/rules?id=tjYW6tntgd)

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category"


class OpenItemCategoryConfigRequest(RestApi):
    """
    获取类目相关配置信息
    更新时间: 2025-06-20 17:03:46
    1.获取类目相关配置信息，返回的类目配置信息的范围与店铺类型相关
    2.店铺类型与类目开放关系详情见文档《快手小店开放类目及资质一览表》(https://www.kwaixiaodian.com/rules?id=tjYW6tntgd)

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category.config&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category.config"


class OpenItemCategoryOptionalGetRequest(RestApi):
    """
    获取商家可选类目列表
    更新时间: 2025-06-20 17:04:57
    获取完整的类目树信息，包含一级类目、二级类目、三级类目和叶子类目的ID及名称，以及当前授权商家的每级类目开通情况

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category.optional.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category.optional.get"


class OpenItemCategoryPropStandardGetRequest(RestApi):
    """
    获取标品模版信息
    更新时间: 2025-06-20 17:06:03
    1、用途：该接口主要用来查询某个类目下标品的模版信息（包括：关键属性、补充属性、标品是否支持图片的信息及填写规则），这些模版信息可以用来申报、纠错标品以及发布商品
    2、接口调用：传入叶子类目ID即可获取模版信息
    3、模版信息使用说明
    3.1、keyPropList中都是关键属性信息，需要关注 commonRuleGroup 字段中的 必填、是否支持自定义输入规则，以及 propAlias 属性别名，inputType 属性输入类型（关键属性只有单选这一种输入类型）
    3.2、spuPropList中都是补充属性信息，需要关注 commonRuleGroup 字段中的 必填、是否支持自定义输入规则，以及 propAlias 属性别名，inputType 属性输入类型（补充属性有单选、多选、文本框 这三种输入类型）
    3.3、standardImageRule表示标品的图片规则，商家申报纠错标品需按要求填写
    4、属性值说明：该接口只会返回属性项信息不会返回属性值信息，查询属性值信息请查询（open.item.category.prop.value.search）接口

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category.prop.standard.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category.prop.standard.get"


class OpenItemCategoryPropValueSearchRequest(RestApi):
    """
    搜索类目属性值
    更新时间: 2025-06-20 17:05:39
    1.搜索类目相关的属性值信息，返回的属性值配置信息的范围与店铺类型相关
    2.店铺类型与类目开放关系详情见文档《快手小店开放类目及资质一览表》

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category.prop.value.search&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category.prop.value.search"


class OpenItemCategoryStandardCheckRequest(RestApi):
    """
    获取标品发品规则
    更新时间: 2025-06-20 17:07:04
    1、用途：该接口主要用来获取标品的发品规则，判断该类目是否可以用来发布标品
    2、接口使用：传入叶子类目ID即可返回对应的发品规则
    3、发品规则说明 ：
    「1-标品强管控」：表示该类目是强管控的，用该类目只能发布标品
    「2-标品弱管控」：表示该类目是弱管控的，既可以用来进行标品发品，也可以进行普通商品发品
    「0-非标品管控」：表示该类目没有配置标品管控规则，不能用来发布标品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category.standard.check&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category.standard.check"


class OpenItemCategoryStandardSearchRequest(RestApi):
    """
    标品信息查询
    更新时间: 2025-06-20 17:07:44
    1、用途：该接口主要是用来查询标品的属性信息（关键属性、绑定属性（SPU属性）、标品图片）、标品ID、类目ID、类目路径、标品状态等
    2、使用方法：
    方法1、输入 叶子类目ID + 标品ID
    方法2、输入 叶子类目ID + 关键属性信息
    3、数据范围：该接口可以查询平台上所有审核通过的标品信息
    Tips：
    1、可以通过接口（open.item.standard.apply.query）查询商家自己申报的标品信息，审核通过的标品可以直接使用
    2、关键属性信息的可以从接口（open.item.category.prop.standard.get）获取

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category.standard.search&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category.standard.search"


class OpenItemCategoryStandardSearchSpuRequest(RestApi):
    """
    标品信息查询（新）
    更新时间: 2025-06-20 17:08:13
    1、用途：该接口主要是用来查询标品的属性信息（关键属性、绑定属性（SPU属性）、标品图片）、标品ID、类目ID、类目路径、标品状态等
    2、使用方法：
    方法1、输入 叶子类目ID + 标品ID
    方法2、输入 叶子类目ID + 关键属性信息
    3、数据范围：该接口可以查询平台上所有审核通过的标品信息
    Tips：
    1、可以通过接口（open.item.standard.apply.query）查询商家自己申报的标品信息，审核通过的标品可以直接使用
    2、关键属性信息的可以从接口（open.item.category.prop.standard.get）获取

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category.standard.search.spu&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category.standard.search.spu"


class OpenItemCategorySuggestedGetRequest(RestApi):
    """
    获取商品类目预测结果
    更新时间: 2025-06-25 10:32:41
    1.根据商品图片、商品标题、商品描述信息获取推荐的发品类目和商家资质开通情况，最多返回三个推荐类目
    2.每个商家每天最多使用2000次

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.category.suggested.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.category.suggested.get"


class OpenItemDeleteRequest(RestApi):
    """
    删除商品
    更新时间: 2025-06-20 17:09:06
    商品处于未上架状态时，允许删除商品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.delete&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.delete"


class OpenItemDeletedGetRequest(RestApi):
    """
    查询7天内已删除的商品
    更新时间: 2025-06-20 17:09:33
    根据商品ID查询7天内已删除的商品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.deleted.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.deleted.get"


class OpenItemDeliveryTimeUpdateRequest(RestApi):
    """
    商品发货时效修改
    更新时间: 2025-06-20 17:09:56
    商品发货时效修改

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.delivery.time.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.delivery.time.update"


class OpenItemDetailImagesUpdateRequest(RestApi):
    """
    更新商品详情图片
    更新时间: 2025-06-20 17:10:22
    1. 最多只能传20张图片
    2. 调用修改图片接口会触发商品送审

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.detail.images.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.detail.images.update"


class OpenItemDetailPageLinkRequest(RestApi):
    """
    获取商品详情页跳转链接
    更新时间: 2025-06-20 17:11:20
    根据商品id跳转到商品详情页，支持直接跳转商品详情页、跳转到直播间再打开商品详情页

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.detail.page.link&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.detail.page.link"


class OpenItemDiagnosisGetRequest(RestApi):
    """
    获取商品质量分
    更新时间: 2025-06-20 17:16:53
    根据商品ID获取商品质量分，商品管理类目必须接入

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.diagnosis.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.diagnosis.get"


class OpenItemEditRequest(RestApi):
    """
    编辑商品
    更新时间: 2025-06-20 17:41:12
    1.当商品状态处于”审核待修改“和”审核通过“状态时允许编辑，其他状态不允许编辑
    2.商品在”通过“状态时，变更名称、详情和商品主图会触发审核
    3.类目变更需要满足当前审核状态为”审核待修改“
    4.返回值列举了当前商品编辑后所有有效的SkuId
    5.多级规格商品修改时遵循和添加商品一致的规则，保持更新之后的商品规格是完整组合即可
    6.若需要对sku规格和规格值进行排序，需指定skuList.skuProps.propSortNum和skuList.skuProps.propValueSortNum的值

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.edit&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.edit"


class OpenItemGetRequest(RestApi):
    """
    获取商品详情
    更新时间: 2025-06-20 17:45:26
    根据商品id获取商家的商品详情，不返回已删除的商品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.get"


class OpenItemImageUploadRequest(RestApi):
    """
    上传商品图片
    更新时间: 2025-06-20 17:12:24
    上传商品主图或商品详情图
    注：Content-Type必须为multipart/form-data;charset=utf-8，否则会被拦截

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.image.upload&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.image.upload"


class OpenItemListGetRequest(RestApi):
    """
    查询商品列表
    更新时间: 2025-06-20 17:13:37
    分页查询商家的商品列表信息，每页返回数最多为100，推荐值为20。

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.list.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.list.get"


class OpenItemMainPicVideoApplyRequest(RestApi):
    """
    应用主图视频至商品
    更新时间: 2025-06-20 17:40:24
    应用主图视频至商品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.main.pic.video.apply&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.main.pic.video.apply"


class OpenItemMainPicVideoDeleteRequest(RestApi):
    """
    删除商品主图视频
    更新时间: 2025-06-20 17:44:20
    删除商品主图视频

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.main.pic.video.delete&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.main.pic.video.delete"


class OpenItemMaterialDetailGetRequest(RestApi):
    """
    查询商品素材详情
    更新时间: 2025-06-20 17:37:02
    查询商品素材详情

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.material.detail.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.material.detail.get"


class OpenItemMaterialUploadTokenIssueRequest(RestApi):
    """
    签发商品素材上传令牌
    更新时间: 2025-06-20 17:31:46
    签发商品素材上传令牌

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.material.upload.token.issue&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.material.upload.token.issue"


class OpenItemMaterialUploadTokenVerifyRequest(RestApi):
    """
    解析校验素材上传令牌
    更新时间: 2025-06-20 17:32:06
    解析校验素材上传令牌

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.material.upload.token.verify&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.material.upload.token.verify"


class OpenItemNewRequest(RestApi):
    """
    新增商品
    更新时间: 2025-06-20 17:44:55
    商家每天创建商品的个数上限为500个，超过当天商品铺货上限时请勿重试

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.new&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.new"


class OpenItemNewPrecheckRequest(RestApi):
    """
    新增商品预校验
    更新时间: 2025-06-20 17:14:48
    商家新增商品前，可以进行店铺与类目维度的前置发品规则预校验

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.new.precheck&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.new.precheck"


class OpenItemOpenItemStandardCorrectSpuRequest(RestApi):
    """
    纠错标品（新）
    更新时间: 2025-06-20 17:18:01
    纠错标品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.open.item.standard.correct.spu&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.open.item.standard.correct.spu"


class OpenItemQualificationCollectionConfigRequest(RestApi):
    """
    获取商品资质采集配置
    更新时间: 2025-06-20 17:21:16
    根据当前叶子类目ID获取当前类目是否需要采集相关资质以及资质配置信息

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.qualification.collection.config&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.qualification.collection.config"


class OpenItemSalepropRuleRequest(RestApi):
    """
    商品销售属性填写规则
    更新时间: 2025-06-20 17:22:20
    商品发布&编辑时，拉取销售属性填写限制

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.saleprop.rule&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.saleprop.rule"


class OpenItemShelfStatusUpdateRequest(RestApi):
    """
    商品上下架管理
    更新时间: 2025-06-20 17:38:19
    1.商品审核状态为通过后，才允许操作商品上架
    2.更改商品的信息都不需要先下架商品，可使用所有编辑商品相关的API实现变更，详情见《已上架商品免审编辑说明》(https://open.kwaixiaodian.com/announcement/detail?cateId=2&pageSign=1628a001aa6be4179348436ccc0f8c641652671830118)
    3.勿频繁操作商品上下架，会影响商品自营和分销效果

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.shelf.status.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.shelf.status.update"


class OpenItemSkuGoodsRelationAddRequest(RestApi):
    """
    新增sku货品关联关系
    更新时间: 2025-06-20 17:21:51
    新增sku与货品关联关系

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.sku.goods.relation.add&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.sku.goods.relation.add"


class OpenItemSkuGoodsRelationDeleteRequest(RestApi):
    """
    删除sku货品关联关系
    更新时间: 2025-06-20 17:23:13
    删除sku与货品关联关系

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.sku.goods.relation.delete&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.sku.goods.relation.delete"


class OpenItemSkuGoodsRelationGetRequest(RestApi):
    """
    获取sku货品关联关系
    更新时间: 2025-06-20 17:22:44
    根据skuId获取sku与货品关联关系

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.sku.goods.relation.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.sku.goods.relation.get"


class OpenItemSkuGoodsRelationUpdateRequest(RestApi):
    """
    更新sku货品关联关系
    更新时间: 2025-06-20 17:24:49
    更新sku与货品关联关系

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.sku.goods.relation.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.sku.goods.relation.update"


class OpenItemSkuListGetRequest(RestApi):
    """
    查询商品sku列表
    更新时间: 2025-06-20 17:25:16
    根据商品id查询商家的商品sku列表全量信息

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.sku.list.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.sku.list.get"


class OpenItemSkuPriceUpdateRequest(RestApi):
    """
    更新在线商品价格
    更新时间: 2025-06-20 17:31:18
    price为long

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.sku.price.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.sku.price.update"


class OpenItemSkuStockUpdateRequest(RestApi):
    """
    更新在线商品库存
    更新时间: 2025-06-20 17:30:57
    1.更新逻辑为增量更新，在原有的库存数量上进行增减
    a.如原有库存为10，要更新库存为18，skuChangeStock值为8，changeType为1(增加库存)；
    b.如原有库存为10,要更新库存为7，skuChangeStock值为3，changeType为2（减少库存）；

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.sku.stock.update&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.sku.stock.update"


class OpenItemStandardApplyRequest(RestApi):
    """
    申报标品
    更新时间: 2025-06-20 17:30:16
    1、用途：该接口主要用来进行标品申报，提交请求后等待运营审核即可，审核通过的标品可以用来进行标品的发布
    2、接口调用说明：
    用户需要传入类目ID、关键属性、补充属性（SPU属性）以及标品图片（可不填，如果配置了标品图片必填那就必须填写）这四部分信息即可完成标品的申报
    3、参数说明
    3.1 categoryId：类目ID，该类目必须是标品管控类目（强、弱管控均可）
    3.2 keyPropList：关键属性信息（必填）
    3.3 spuPropList：补充属性信息
    3.4 standardImages：标品图片（图片必须是快手图片，见Tips3）
    Tips：
    1、获取属性信息（关键、补充属性）以及填写规则：open.item.category.prop.standard.get
    2、属性值信息：open.item.category.prop.value.search
    3、转化为快手图片：open.item.image.upload

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.standard.apply&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.standard.apply"


class OpenItemProductStandardApplySearchRequest(RestApi):
    """
    搜索标品申报列表
    更新时间: 2025-06-20 17:29:56
    1、用途：该接口用来查询商家自己申报以及纠错的标品信息（关键、绑定属性、标品图片、类目路径等），审核通过的标品可以用来发品
    2、接口调用：输入类目ID、以及其他的相关条件即可分页批量查询用户自己申报纠错的标品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.standard.apply.query&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.standard.apply.query"


class OpenItemStandardApplyQuerySpuRequest(RestApi):
    """
    搜索标品申报列表（新）
    更新时间: 2025-06-20 17:29:11
    1、用途：该接口用来查询商家自己申报以及纠错的标品信息（关键、绑定属性、标品图片、类目路径等），审核通过的标品可以用来发品
    2、接口调用：输入类目ID、以及其他的相关条件即可分页批量查询用户自己申报纠错的标品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.standard.apply.query.spu&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.standard.apply.query.spu"


class OpenItemStandardApplySpuRequest(RestApi):
    """
    申报标品（新）
    更新时间: 2025-06-20 17:28:37
    1、用途：该接口主要用来进行标品申报，提交请求后等待运营审核即可，审核通过的标品可以用来进行标品的发布
    2、接口调用说明：
    用户需要传入类目ID、关键属性、补充属性（SPU属性）以及标品图片（可不填，如果配置了标品图片必填那就必须填写）这四部分信息即可完成标品的申报
    3、参数说明
    3.1 categoryId：类目ID，该类目必须是标品管控类目（强、弱管控均可）
    3.2 keyPropList：关键属性信息（必填）
    3.3 spuPropList：补充属性信息
    3.4 standardImages：标品图片（图片必须是快手图片，见Tips3）
    Tips：
    1、获取属性信息（关键、补充属性）以及填写规则：open.item.category.prop.standard.get
    2、属性值信息：open.item.category.prop.value.search
    3、转化为快手图片：open.item.image.upload

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.standard.apply.spu&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.standard.apply.spu"


class OpenItemStandardCorrectRequest(RestApi):
    """
    纠错标品
    更新时间: 2025-06-20 17:28:15
    纠错标品

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.standard.correct&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.standard.correct"


class OpenItemVideoCaptionEditRequest(RestApi):
    """
    修改商品视频标题
    更新时间: 2025-06-20 17:39:23
    修改商品视频标题

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.video.caption.edit&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.video.caption.edit"


class OpenItemVideoCountRequest(RestApi):
    """
    查询商家视频总数
    更新时间: 2025-06-20 17:43:24
    查询商家视频总数

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.video.count&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.video.count"


class OpenItemVideoDeleteRequest(RestApi):
    """
    商家视频删除
    更新时间: 2025-06-20 17:40:51
    商家视频删除

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.video.delete&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.video.delete"


class OpenItemVideoInfoRequest(RestApi):
    """
    查询商品视频详情
    更新时间: 2025-06-20 17:37:28
    查询商品视频详情

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.video.info&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.video.info"


class OpenItemVideoListRequest(RestApi):
    """
    查询商家视频列表
    更新时间: 2025-06-20 17:39:59
    查询商家视频列表

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.item.video.list&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.item.video.list"
