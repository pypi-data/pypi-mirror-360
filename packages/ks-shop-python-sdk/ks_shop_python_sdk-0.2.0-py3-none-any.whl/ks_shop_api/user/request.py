# -*- coding: utf-8 -*-
import deprecation
from ks_shop_api.base import RestApi
"""
用户API
"""


class OpenUserFansCheckRequest(RestApi):
    """
    校验用户是否为粉丝
    更新时间: 2023-02-02 15:44:11
    校验openId所属的用户是否为当前授权方的粉丝

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.user.fans.check&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.user.fans.check"


class OpenUserInfoGetRequest(RestApi):
    """
    获取用户公开信息
    更新时间: 2022-07-28 20:47:54
    获取用户公开信息

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.user.info.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.user.info.get"


class OpenUserSellerGetRequest(RestApi):
    """
    获取商家信息
    更新时间: 2021-12-21 11:35:35
    获取商家信息api

    https://open.kwaixiaodian.com/zone/new/docs/api?name=open.user.seller.get&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "open.user.seller.get"
