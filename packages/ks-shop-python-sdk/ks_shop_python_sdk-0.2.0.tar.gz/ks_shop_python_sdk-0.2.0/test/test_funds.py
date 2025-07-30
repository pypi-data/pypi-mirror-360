import sys
from pathlib import Path
# 将项目根目录添加到 sys.path
root_dir = Path(__file__).parent.parent  # 根据文件位置调整层级
sys.path.insert(0,str(root_dir))

from ks_shop_api.funds import request
from ks_shop_api.funds import schema
from test.test_base import base_request

def test_center_account_info():
    """
    Test function for CenterAccountInfoRequest.OpenFunds
    """
    params = schema.OpenFundsCenterAccountInfoSchema()
    response = base_request(request.OpenFundsCenterAccountInfoRequest, params=params)
    print(response)
# test_center_account_info()

def test_center_get_daily_bill():
    """
    Test function for CenterGetDailyBillRequest.OpenFunds
    """
    params = schema.OpenFundsCenterGetDailyBillSchema()
    params.billDate = '20250601'
    params.billType = '1'
    response = base_request(request.OpenFundsCenterGetDailyBillRequest, params=params)
    print(response)
# test_center_get_daily_bill()

def test_center_get_depositinfo():
    """
    Test function for CenterGetDepositinfoRequest.OpenFunds
    """
    params = schema.OpenFundsCenterGetDepositinfoSchema()
    params.securityDepositType = 1
    response = base_request(request.OpenFundsCenterGetDepositinfoRequest, params=params)
    print(response)
# test_center_get_depositinfo()

def test_center_get_withdraw_result():
    """
    Test function for CenterGetWithdrawResultRequest.OpenFunds
    """
    params = schema.OpenFundsCenterGetWithdrawResultSchema()
    params.withdrawNo = 'SWW751460602547675168'
    params.accountChannel = 4
    response = base_request(request.OpenFundsCenterGetWithdrawResultRequest, params=params)
    print(response)
# test_center_get_withdraw_result()

def test_center_withdraw_record_list():
    """
    Test function for CenterWirhdrawRecordListRequest.OpenFunds
    """
    params = schema.OpenFundsCenterWirhdrawRecordListSchema()
    params.limit = 10
    params.createTimeStart = 1746089690000
    params.page = 1
    params.accountChannel = 4
    params.createTimeEnd = 1750409794894
    params.subMerchantId = '5504000268423236'
    response = base_request(request.OpenFundsCenterWirhdrawRecordListRequest, params=params)
    print(response)
# test_center_withdraw_record_list()

if __name__ == '__main__':
    pass
