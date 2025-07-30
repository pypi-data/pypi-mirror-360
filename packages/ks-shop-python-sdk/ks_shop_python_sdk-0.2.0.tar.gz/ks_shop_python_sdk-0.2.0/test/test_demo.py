# -*- coding: utf-8 -*-
from ks_shop_api.funds.request import OpenFundsCenterAccountInfoRequest
from ks_shop_api.funds.schema import OpenFundsCenterAccountInfoSchema
from ks_shop_api.schema import baseAppInfoSchema


if __name__ == '__main__':
    access_token = 'ChFvYXV0aC5hY2Nlc3NUb2tlbhJwpNpb7eMgFXs96eIOV8IFSx12GgxBaSF30EX1mz_5wmhHdP3G1LY259-y6ttEX4_K_AYpIkJKI0S35XznxCWLKZGo7bduz0RGQKIQw4HCla6VfHEn5xjuKYp_MXa8y9fkn1h0xYoW9ls3liwXF9aabxoScAL-5UOESPmGw1rbq86lMYBWIiBnVJKChf3PXDepPbsDIOwB1r3OK6I9QxD2B2Mt_cuCwSgFMAE'
    base_app_info = baseAppInfoSchema()
    base_app_info.app_key = "ks653021946718290428"
    base_app_info.secret = "ft9b-ITeSl4qooSGxrdTMQ"
    base_app_info.sign_secret = "dc90166e66aa4a4a5921bf0e2941a4fe"
    print(base_app_info)
    ks_obj = OpenFundsCenterAccountInfoRequest(**base_app_info.model_dump())
    ks_schema = OpenFundsCenterAccountInfoSchema()
    print(ks_schema)
    print(ks_schema.model_dump())

    res = ks_obj.getResponse(access_token, params=ks_schema)
    print(res)
