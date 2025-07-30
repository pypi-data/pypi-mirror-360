# -*- coding: utf-8 -*-
import deprecation
from ks_shop_api.base import RestApi
"""
账单API
"""

class OpenFundsCenterAccountInfoRequest(RestApi):
    """
    查询现金户
    更新时间: 2023-11-15 14:38:21
    查询商家现金户状态和余额，渠道包括小店余额、微信、支付宝和安心钱包

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.center.account.info&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.center.account.info"


@deprecation.deprecated(details="待下线，请使用open.funds.financial.settled.bill.detail查询账单信息（新)")
class OpenFundsCenterGetDailyBillRequest(RestApi):
    """
    下载日账单（待下线）
    更新时间: 2024-05-21 16:09:13
    「待下线，请使用open.funds.financial.settled.bill.detail查询账单信息（新)」
    下载商家日账单，首次请求会触发文件生成，需要轮询获取状态，状态为成功时才会生成下载地址;

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.center.get.daily.bill&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.center.get.daily.bill"


class OpenFundsCenterGetDepositinfoRequest(RestApi):
    """
    查询保证金余额
    更新时间: 2024-10-24 17:48:27
    查询商家保证金余额

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.center.get.depositinfo&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.center.get.depositinfo"


class OpenFundsCenterGetWithdrawResultRequest(RestApi):
    """
    查询现金户提现申请结果
    更新时间: 2023-08-10 10:53:20
    查询现金户提现申请结果（支持小店余额和安心钱包提现申请结果，微信和支付宝提现结果查询时暂不支持）

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.center.get.withdraw.result&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.center.get.withdraw.result"


class OpenFundsCenterWirhdrawRecordListRequest(RestApi):
    """
    查询现金户提现列表
    更新时间: 2024-12-19 16:39:32
    查询商家现金户提现的记录列表

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.center.wirhdraw.record.list&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.center.wirhdraw.record.list"


class OpenFundsCenterWithdrawApplyRequest(RestApi):
    """
    申请现金户提现
    更新时间: 2025-01-06 11:37:09
    申请商家现金户提现（小店余额暂不支持提现）

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.center.withdraw.apply&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.center.withdraw.apply"


@deprecation.deprecated(details="待下线，请使用open.funds.financial.settled.bill.detail(获取账单信息v2)")
class OpenFundsFinancialBillBatchDetailRequest(RestApi):
    """
    普通账单数据（待下线）
    更新时间: 2023-10-31 10:44:32
    待下线，请使用open.funds.financial.settled.bill.detail(获取账单信息v2)

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.bill.batch.detail&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.bill.batch.detail"


@deprecation.deprecated(details="待下线，请使用open.funds.financial.settled.bill.detail(获取账单信息v2)")
class OpenFundsFinancialBillDetailRequest(RestApi):
    """
    账单详情信息（待下线）
    更新时间: 2023-10-31 10:47:01
    待下线，请使用open.funds.financial.settled.bill.detail(获取账单信息v2)

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.bill.detail&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.bill.detail"


class OpenFundsFinancialBillLogisticsProviderQueryRequest(RestApi):
    """
    物流供应商账单明细
    更新时间: 2025-03-24 10:50:04
    物流供应商账单明细，只包括已结算账单

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.bill.logistics.provider.query&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.bill.logistics.provider.query"


class OpenFundsFinancialBillPostSalesListRequest(RestApi):
    """
    查询超售后期账单列表
    更新时间: 2025-05-29 11:38:40
    查询超售后期账单列表

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.bill.post.sales.list&version=1
    """
    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.bill.post.sales.list"


class OpenFundsFinancialBillPostSalesListRequest(RestApi):
    """
    查询达人钱包账单（平安、聚力）
    更新时间: 2025-01-13 15:38:10
    查询达人钱包账单（平安、聚力），暂时只支持达人钱包账单查询，达人钱包账单包括达人钱包提现、达人钱包收入、达人钱包支出等

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.bill.query.account&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.bill.query.account"


class OpenFundsFinancialFreightInsuranceListRequest(RestApi):
    """
    查询运费险扣费明细
    更新时间: 2025-01-16 16:26:37
    查询商家运费险扣费明细

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.freight.insurance.list&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.freight.insurance.list"


class OpenFundsFinancialPinganBillRequest(RestApi):
    """
    查询安心钱包账务明细
    更新时间: 2024-09-10 16:52:24
    查询安心钱包账务明细
    商家如果开通安心钱包，后续货款结算都会到安心钱包。
    查询安心钱包账务明细包含货款结算，还有余额提现，补结算等场景。

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.pingan.bill&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.pingan.bill"


class OpenFundsFinancialQueryBillListRequest(RestApi):
    """
    查询达人账单列表
    更新时间: 2025-04-08 16:29:39
    导出场景，根据账单类型查询账单列表。

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.query.bill.list&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.query.bill.list"


class OpenFundsFinancialSettledBillDetailRequest(RestApi):
    """
    查询账单信息（新）
    更新时间: 2025-04-07 19:44:26
    查询商家账单信息，支持基于order_id的单个查询和基于结算时间的批量订单查询

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.settled.bill.detail&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.settled.bill.detail"


class OpenFundsFinancialStatementListRequest(RestApi):
    """
    查询货款账单明细
    更新时间: 2024-07-05 11:27:23
    查询商家货款账单明细 (只有安心钱包渠道)
    查询货款账单明细只有货款结算的账单
    在安心钱包账单的基础上，扩展了一些账单计费项的数据。

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.financial.statement.list&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.financial.statement.list"


class OpenFundsPlatformCenterAgreementBillDownloadRequest(RestApi):
    """
    辛选年框账单下载
    更新时间: 2025-04-10 19:50:14
    辛选年框账单下载，仅用于获取下载链接

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.platform.center.agreement.bill.download&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.platform.center.agreement.bill.download"


class OpenFundsSubsidyAuditInvoiceInfoRequest(RestApi):
    """
    国补消费者发票信息查询接口
    更新时间: 2025-03-20 19:37:36
    国补消费者发票信息查询接口

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.subsidy.audit.invoice.info&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.subsidy.audit.invoice.info"


class OpenFundsSubsidyOpenApplyInvoiceRequest(RestApi):
    """
    国补审计提交发票
    更新时间: 2025-06-12 16:47:20
    国补审计提交发票

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.subsidy.open.apply.invoice&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.subsidy.open.apply.invoice"


class OpenFundsSubsidyOpenApplyInvoiceFileRequest(RestApi):
    """
    国补审计提交发票附带文件
    更新时间: 2025-06-12 16:48:22
    国补审计提交发票附带文件
    调用方式见：https://docs.qingque.cn/d/home/eZQBHsmmNHWDQ2VF6_zr4Zjzo?identityId=1zcQPfssrKt

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.funds.subsidy.open.apply.invoice.file&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.funds.subsidy.open.apply.invoice.file"
