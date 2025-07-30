##### 安装
```sh
pip install  ks-shop-python-sdk
```

##### 获取access_token
```python
from ks_shop_api.utils import get_access_token_by_code, refresh_access_token


app_id = "xxxx"  # 应用ID
app_secret = "xxxx"  # 应用密钥
code = "xxxx"  # 首次授权通过回调地址中的code
first_res = get_access_token_by_code(app_id, app_secret, code)
print(first_res)


refresh_token = "xxxxx"  # 刷新令牌
refresh_res = refresh_access_token(app_id, app_secret, refresh_token)
print(refresh_res)
```


##### 使用
```python
from ks_shop_api.funds.request import OpenFundsCenterAccountInfoRequest
from ks_shop_api.funds.schema import OpenFundsCenterAccountInfoSchema
from ks_shop_api.schema import baseAppInfoSchema


access_token = 'xxxx'
base_app_info = baseAppInfoSchema()
base_app_info.app_key = "xxxx"
base_app_info.secret = "xxxx"
base_app_info.sign_secret = "xxxx"
print(base_app_info)
ks_obj = OpenFundsCenterAccountInfoRequest(**base_app_info.model_dump())

ks_schema = OpenFundsCenterAccountInfoSchema()
print(ks_schema)
print(ks_schema.model_dump())

res = ks_obj.getResponse(access_token, params=ks_schema)
print(res)


######或者 dict########
access_token = 'xxxx'
app_info = {
    "app_key": "xxxx",
    "secret": "xxxx",
    "sign_secret": "xxxx"
}
ks_obj: RestApi = OpenFundsCenterAccountInfoRequest(**app_info)

params = {}
res = ks_obj.getResponse(access_token, params=params)
print(res)
```
