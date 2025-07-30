# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, List

class OpenFundsCenterAccountInfoSchema(BaseModel):
    pass


class OpenFundsCenterGetDailyBillSchema(BaseModel):
    billDate: Optional[str] = Field(default=None, description="账单日期， 格式：yyyyMMdd")
    billType: Optional[str] = Field(default=None, description="账单类型， 1 货款日账单 2 小额打款日账单 3 履约日账单 4 商户已结算日账单下载")
    expireDate: Optional[int] = Field(default=None, description="有效期，单位 小时 默认 168小时（ 保存7天 ）范围 24-720 文件过期后再申请会重新生成新文件")


class OpenFundsCenterGetDepositinfoSchema(BaseModel):
    securityDepositType: Optional[int] = Field(default=None, description="保证金类型 （自建保证金1，推广保证金2，跨境保证金7)")


class OpenFundsCenterGetWithdrawResultSchema(BaseModel):
    withdrawNo: Optional[str] = Field(default=None, description="业务提现号")
    accountChannel: Optional[int] = Field(default=None, description="提现渠道 （1 小店余额 2 微信 3 支付宝 4 安心钱包）")


class OpenFundsCenterWirhdrawRecordListSchema(BaseModel):
    limit: Optional[int] = Field(default=None, description="页数限制")
    createTimeStart: Optional[int] = Field(default=None, description="时间范围")
    page: Optional[int] = Field(default=None, description="页码")
    accountChannel: Optional[int] = Field(default=None, description="提现渠道 （1 小店余额 2 微信 3 支付宝 4 安心钱包）")
    createTimeEnd: Optional[int] = Field(default=None, description="时间范围")
    subMerchantId: Optional[str] = Field(default=None, description="二级商户号")


class OpenFundsCenterWithdrawApplySchema(BaseModel):
    withdrawMoney: Optional[float] = Field(default=None, description="提现金额")
    withdrawNo: Optional[str] = Field(default=None, description="业务提现单号")
    remark: Optional[str] = Field(default=None, description="提现备注")
    accountChannel: Optional[int] = Field(default=None, description="提现渠道 （1 小店余额 2 微信 3 支付宝 4 安心钱包）")
    subMerchantId: Optional[str] = Field(default=None, description="	二级商户号 （微信、支付宝，安心钱包 传入）")


class OpenFundsFinancialBillBatchDetailSchema(BaseModel):
    cursor: Optional[str] = Field(default=None, description="游标，第一次请求不传，后续请求传入上次返回的游标")
    settlementEndTime: Optional[int] = Field(default=None, description="商户的结算结束时间")
    settlementStartTime: Optional[int] = Field(default=None, description="商户的结算开始时间")


class OpenFundsFinancialBillDetailSchema(BaseModel):
    orderId: Optional[str] = Field(default=None, description="订单ID")


class OpenFundsFinancialBillLogisticsProviderQuerySchema(BaseModel):
    cursor: Optional[str] = Field(default=None, description="游标，第一次请求不传，后续请求传入上次返回的游标")
    settlementTimeEnd: Optional[int] = Field(default=None, description="结算时间-结束（包含）")
    orderCreateTimeStart: Optional[int] = Field(default=None, description="订单创建时间-开始（包含），时间间隔不超过1天")
    orderCreateTimeEnd: Optional[int] = Field(default=None, description="订单创建时间-结束（包含）")
    settlementTimeStart: Optional[int] = Field(default=None, description="结算时间-开始（包含），时间间隔不超过1天")
    orderId: Optional[str] = Field(default=None, description="订单ID")


class OpenFundsFinancialBillPostSalesListSchema(BaseModel):
    cursor: Optional[str] = Field(default=None, description="游标，第一次请求不传，后续请求传入上次返回的游标")
    startTime: Optional[int] = Field(default=None, description="退款完成开始时间")
    endTime: Optional[int] = Field(default=None, description="退款完成结束时间")


class OpenFundsFinancialBillPostSalesListSchema(BaseModel):
    cursor: Optional[str] = Field(default=None, description="游标 （第一页不传，从第二页开始写上一页的返回值，默认每页100条）")
    startTime: Optional[int] = Field(default=None, description="开始时间 左闭右开，最大时间范围为1天")
    roleType: Optional[str] = Field(default=None, description="角色类型：达人DISTRIBUTOR、商家SELLER")
    bizType: List[str] = Field(default=None, description="业务类型 （不传查全部）SETTLE (货款结算),WITHDRAW (余额提现),WITHDRAW_FAIL (余额提现失败),MARGIN_SETTLE (差额结算),SUBSIDY_RETURN (补差退回),SUBSIDY_RETURN_FAIL (补差退回失败),COMMISSION_RETURN (分账退回),REFUND (结算后退款),REFUND_FAIL (退款失败),FUND_FREEZE (资金冻结),FUND_UNFREEZE (资金解冻),FUND_TRANSFER (资金转账),FUND_TRANSFER_FAIL (资金转账失败),FUND_DEDUCT (资金扣减),FUND_DEDUCT_FAIL (资金扣减失败),FUND_DEDUCT_RETURN (资金扣减回退),FUND_UNFREEZE_DEDUCT (资金解冻并扣款),FUND_UNFREEZE_TEMPORARY (资金临时解冻),MARGIN_SETTLE（补结算),SUBSIDY_RETURN_FAIL（补贴扣除失败）")
    endTime: Optional[int] = Field(default=None, description="截止时间 左闭右开，最大时间范围为1天")
    walletType: Optional[str] = Field(default=None, description="钱包类型：5:安心钱包、18:聚力钱包、23:支付宝、24:微信")
    subMchId: Optional[str] = Field(default=None, description="	商户号，非必填。安心钱包/聚力钱包可以不填，支付宝/微信账单必填")


class OpenFundsFinancialFreightInsuranceListSchema(BaseModel):
    cursor: Optional[str] = Field(default=None, description="游标，上一次请求的cursor值，首次查询无需传值")
    startCompleteTime: Optional[int] = Field(default=None, description="扣款成功开始时间")
    endCompleteTime: Optional[int] = Field(default=None, description="扣款成功结束时间")


class OpenFundsFinancialPinganBillSchema(BaseModel):
    cursor: Optional[str] = Field(default=None, description="游标 （第一页不传，从第二页开始填写上一页的返回值，默认每页20条）")
    startTime: Optional[int] = Field(default=None, description="账务日期开始 （仅支持过去6个月内的日期查询）")
    endTime: Optional[int] = Field(default=None, description="账务日期截止（最早只能查到上一日数据）")
    bizType: List[str] = Field(default=None, description="""业务类型 （不传查全部） FUND_UNFREEZE_TEMPORARY(扣减前临时解冻) COMMISSION_RETURN_DEDUCT(佣金返还) SETTLE(货款结算) WITHDRAW(余额提现) WITHDRAW_FAIL(提现失败) MARGIN_SETTLE(补结算) SUBSIDY_RETURN(补贴扣除) SUBSIDY_RETURN_FAIL(补贴扣除失败) COMMISSION_RETURN(佣金/技术服务费返还) REFUND(结算后退款) REFUND_FAIL(结算后退款失败) FUND_FREEZE(资金冻结) FUND_UNFREEZE(资金解冻) FUND_TRANSFER(资金转账) FUND_TRANSFER_FAIL(资金转账失败) FUND_DEDUCT(资金扣减) FUND_DEDUCT_FAIL(资金扣减失败) FUND_DEDUCT_RETURN(资金扣减回退) COMMON_REWARD(资金转入) COMMON_FUND_TAKE_BACK(资金转入回退) COMMON_WITHDRAW(余额提现)""" )
    subMchId: Optional[str] = Field(default=None, description="安心钱包ID （可不填写，默认查询当前生效中的安心钱包。若无数据，请检查安心钱包是否已经变更，请传入旧的安心钱包id再进行查询）")


class OpenFundsFinancialQueryBillListSchema(BaseModel):
    endTime: Optional[int] = Field(default=None, description="截止时间 左闭右闭区间，最大时间范围小于1天")
    scrollId: Optional[str] = Field(default=None, description="游标，第一次请求不传，后续请求传入上次返回的游标")
    orderStatus: Optional[int] = Field(default=None, description="订单状态：0全部，30待发货，40已发货，50已签收，70交易完成")
    startTime: Optional[int] = Field(default=None, description="开始时间 左闭右闭区间，最大时间范围小于1天")
    billType: Optional[str] = Field(default=None, description="账单类型：6：达人未结算账单，7：达人已结算账单")
    accountChannel: List[str] = Field(default=None, description="	渠道类型：微信：WECHAT，支付宝：ALIPAY_ZFT，平安：PINGAN_JZB")


class OpenFundsFinancialSettledBillDetailSchema(BaseModel):
    cursor: Optional[str] = Field(default=None, description="游标，第一个数字表示订单创建时间，第二个数字表示订单号")
    settlementStartTime: Optional[int] = Field(default=None, description="结算开始时间，根据时间范围批量查询时与账单完成时间必填一个")
    settlementEndTime: Optional[int] = Field(default=None, description="结算结束时间，根据时间范围批量查询时与账单完成时间必填一个")
    orderId: Optional[int] = Field(default=None, description="订单号，根据订单号查询时必填")
    size: Optional[int] = Field(default=None, description="	分页尺寸，默认为10")
    orderCompleteStartTime: Optional[int] = Field(default=None, description="账单完成时间开始，根据时间范围批量查询时，与结算时间必填一个")
    orderCompleteEndTime: Optional[int] = Field(default=None, description="账单完成时间结束，根据时间范围批量查询时，与结算时间必填一个")


class OpenFundsFinancialStatementListSchema(BaseModel):
    cursor: Optional[str] = Field(default=None, description="游标 （第一页不传，从第二页开始填写上一页的返回值，默认每页20条）")
    startTime: Optional[int] = Field(default=None, description="账务日期开始 （仅支持过去6个月内的日期查询）")
    endTime: Optional[int] = Field(default=None, description="账务日期截止（最早只能查到上一日数据）")
    subMchId: Optional[str] = Field(default=None, description="安心钱包ID （可不填写，默认查询当前生效中的安心钱包）")


class OpenFundsPlatformCenterAgreementBillDownloadSchema(BaseModel):
    date: Optional[int] = Field(default=None, description="	指定的下载日期，yyyyMMdd格式")


class OpenFundsSubsidyAuditInvoiceInfoSchema(BaseModel):
    oid: Optional[str] = Field(default=None, description="快手订单号")


class InvoiceDetailInfoProto(BaseModel):
    amount: Optional[float] = Field(default=None, description="发票金额")
    certNo: Optional[str] = Field(default=None, description="销售方纳税人识别号，如果是供销模式，传供应商纳税人识别号")
    invoiceLocationCode: Optional[str] = Field(default=None, description="参加江苏省国补的订单必填，填区级对应的6位行政区划代码https: // www.mca.gov.cn/mzsj/xzqh/2023/202301xzqh.html如：江苏省-南京市-玄武区，填320102")
    fileName: Optional[str] = Field(default=None, description="文件名称")
    invoiceNo: Optional[str] = Field(default=None, description="发票号码")
    invoiceOpenDate: Optional[int] = Field(default=None, description="发票开具日期")
    taxAuthorityCode: Optional[str] = Field(default=None, description="""
                                                                    参加江苏省国补的订单必填
                                                                    税务机构代码查询指引：
                                                                    1. 电子税务局查询：
                                                                    登录“国家税务总局电子税务局”官网，进入“我要查询”-“税务机关信息”。
                                                                    2. 电话咨询：
                                                                    拨打12366纳税服务热线，提供所在地区名称获取代码。
                                                                    3. 实地查询：
                                                                    前往当地税务局办事大厅，通过窗口或自助终端查询。
                                                                    """)
    count: Optional[int] = Field(default=None, description="数量")
    goods: Optional[str] = Field(default=None, description="货物或应税劳务服务名称（含型号）")
    invoiceCode: Optional[str] = Field(default=None, description="发票代码；增值税普票必传")
    fileKey: Optional[str] = Field(default=None, description="文件key（不传）")
    invoiceForeverUrl: Optional[str] = Field(default=None, description="发票链接：仅支持pdf或者ofd格式")
    excludeTaxAmount: Optional[str] = Field(default=None, description="发票不含税金额（单位元）")
    invoiceVerifyCode: Optional[str] = Field(default=None, description="发票校验码；增值税普票必传")
    safeFileKey: Optional[str] = Field(default=None, description="安全文件key（不传）")
    invoiceTax: Optional[str] = Field(default=None, description="发票税额（单位元）")


class OpenFundsSubsidyOpenApplyInvoiceSchema(BaseModel):
    amount: Optional[int] = Field(default=None, description="开票金额（不传，系统自动计算）")
    relateOrderNo: Optional[str] = Field(default=None, description="同快手电商开放平台-快手电商官网 里的oid")
    invoiceType: Optional[int] = Field(default=None, description="	发票形式（电子），固定传1")
    invoiceOpenKind: Optional[int] = Field(default=None, description="发票类型：增值税普票传1，数电普票传3")
    electronInvoiceInfoList: Optional[List[InvoiceDetailInfoProto]] = Field(default=None, description="发票列表（只能传1张发票信息）")
    taxRate: Optional[str] = Field(default=None, description="如13%税率，传13即可")
    token: Optional[str] = Field(default=None, description="token（不填）")


class OpenFundsSubsidyOpenApplyInvoiceFileSchema(BaseModel):
    relateOrderNo: Optional[str] = Field(default=None, description="同快手电商开放平台-快手电商官网 里的oid")
    invoiceOpenKind: Optional[int] = Field(default=None, description="发票类型：增值税普票传1，数电普票传3")
    taxRate: Optional[str] = Field(default=None, description="如13%税率，传13即可")
    certNo: Optional[str] = Field(default=None, description="销售方纳税人识别号，如果是供销模式，传供应商纳税人识别号")
    invoiceName: Optional[str] = Field(default=None, description="发票文件原始名称，图片或者pdf")
    invoiceOpenDate: Optional[int] = Field(default=None, description="发票开具日期")
    invoiceBytes: Optional[bytes] = Field(default=None, description="发票文件二进制信息。Content-Type必须使用multipart/form-data;charset=utf-8传入数据，此字段为参数顶层，按照图片字节数组（不是base64）方式传入。可以点击上传商品图片接口请求示例查看")
    count: Optional[int] = Field(default=None, description="数量")
    goods: Optional[str] = Field(default=None, description="货物或应税劳务服务名称（含型号）")
    invoiceCode: Optional[str] = Field(default=None, description="发票代码；增值税普票必传")
    invoiceVerifyCode: Optional[str] = Field(default=None, description="发票校验码；增值税普票必传")
    invoiceTax: Optional[str] = Field(default=None, description="发票税额（单位元）")
    taxAuthorityCode: Optional[str] = Field(default=None, description="""
                                                                    参加江苏省国补的订单必填
                                                                    税务机构代码查询指引：
                                                                    1. 电子税务局查询：
                                                                    登录“国家税务总局电子税务局”官网，进入“我要查询”-“税务机关信息”。
                                                                    2. 电话咨询：
                                                                    拨打12366纳税服务热线，提供所在地区名称获取代码。
                                                                    3. 实地查询：
                                                                    前往当地税务局办事大厅，通过窗口或自助终端查询。
                                                                    """)
    invoiceLocationCode: Optional[str] = Field(default=None, description="参加江苏省国补的订单必填，填区级对应的6位行政区划代码https: // www.mca.gov.cn/mzsj/xzqh/2023/202301xzqh.html如：江苏省-南京市-玄武区，填320102")
    excludeTaxAmount: Optional[str] = Field(default=None, description="发票不含税金额（单位元）")
    isvCode: Optional[str] = Field(default=None, description="平台下发的业务code")
    invoiceNo: Optional[str] = Field(default=None, description="发票号码")
