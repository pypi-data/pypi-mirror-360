import sys
from pathlib import Path
# 将项目根目录添加到 sys.path
root_dir = Path(__file__).parent.parent  # 根据文件位置调整层级
sys.path.insert(0,str(root_dir))

from ks_shop_api.base import RestApi
from pydantic import BaseModel
from ks_shop_api.schema import baseAppInfoSchema
from ks_shop_api.funds import request
from ks_shop_api.funds import schema


def base_request(req: RestApi, params: dict | BaseModel={}):
    """
    Test function for RestApi requests.
    """
    access_token = 'ChFvYXV0aC5hY2Nlc3NUb2tlbhJwpNpb7eMgFXs96eIOV8IFSx12GgxBaSF30EX1mz_5wmhHdP3G1LY259-y6ttEX4_K_AYpIkJKI0S35XznxCWLKZGo7bduz0RGQKIQw4HCla6VfHEn5xjuKYp_MXa8y9fkn1h0xYoW9ls3liwXF9aabxoScAL-5UOESPmGw1rbq86lMYBWIiBnVJKChf3PXDepPbsDIOwB1r3OK6I9QxD2B2Mt_cuCwSgFMAE'
    base_app_info = baseAppInfoSchema()
    base_app_info.app_key = "ks653021946718290428"
    base_app_info.secret = "ft9b-ITeSl4qooSGxrdTMQ"
    base_app_info.sign_secret = "dc90166e66aa4a4a5921bf0e2941a4fe"
    req_obj: RestApi = req(**base_app_info.model_dump())
    try:
        response = req_obj.getResponse(access_token, params=params)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")

def test_center_account_info():
    """
    Test function for CenterAccountInfoRequest.
    """
    params = schema.CenterAccountInfoSchema()
    response = base_request(request.CenterAccountInfoRequest, params=params)
    print(response)
# test_center_account_info()

def test_center_get_daily_bill():
    """
    Test function for CenterGetDailyBillRequest.
    """
    params = schema.CenterGetDailyBillSchema()
    params.billDate = '20250601'
    params.billType = '1'
    response = base_request(request.CenterGetDailyBillRequest, params=params)
    print(response)
# test_center_get_daily_bill()

def test_center_get_depositinfo():
    """
    Test function for CenterGetDepositinfoRequest.
    """
    params = schema.CenterGetDepositinfoSchema()
    params.securityDepositType = 1
    response = base_request(request.CenterGetDepositinfoRequest, params=params)
    print(response)
# test_center_get_depositinfo()

def test_center_get_withdraw_result():
    """
    Test function for CenterGetWithdrawResultRequest.
    """
    params = schema.CenterGetWithdrawResultSchema()
    params.withdrawNo = 'SWW751460602547675168'
    params.accountChannel = 4
    response = base_request(request.CenterGetWithdrawResultRequest, params=params)
    print(response)
# test_center_get_withdraw_result()

def test_center_withdraw_record_list():
    """
    Test function for CenterWirhdrawRecordListRequest.
    """
    params = schema.CenterWirhdrawRecordListSchema()
    params.limit = 10
    params.createTimeStart = 1746089690000
    params.page = 1
    params.accountChannel = 4
    params.createTimeEnd = 1750409794894
    params.subMerchantId = '5504000268423236'
    response = base_request(request.CenterWirhdrawRecordListRequest, params=params)
    print(response)
# test_center_withdraw_record_list()

if __name__ == '__main__':
    pass
