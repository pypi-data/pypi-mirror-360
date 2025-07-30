
from ks_shop_api.utils import get_access_token_by_code, refresh_access_token


app_id = "xxxx"  # 应用ID
app_secret = "xxxx"  # 应用密钥
code = "xxxx"  # 首次授权通过回调地址中的code

first_res = get_access_token_by_code(app_id, app_secret, code)
print(first_res)

refresh_token = "xxxxx"

refresh_res = refresh_access_token(app_id, app_secret, refresh_token)
print(refresh_res)

