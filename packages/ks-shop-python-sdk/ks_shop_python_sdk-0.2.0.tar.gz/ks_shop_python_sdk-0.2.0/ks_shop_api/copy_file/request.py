# -*- coding: utf-8 -*-
import deprecation
from ks_shop_api.base import RestApi
"""
xxxxxx API
"""


class XXXXXXRequest(RestApi):
    """
    xxxxxx
    xxxxxx
    xxxxxx

    https://open.kwaixiaodian.com/zone/new/docs/api?name=xxxxxxxxx&version=1
    """

    def __init__(self, app_key, secret, sign_secret):
        super().__init__(app_key, secret, sign_secret)

    def get_api_name(self):
        return "xxxxxxxxx"
