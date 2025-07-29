
import httpx
"""
快手电商开放平台
https://open.kwaixiaodian.com/zone/new/docs/api
"""

def get_access_token_by_code(app_id, app_secret, code, grant_type="code"):
    """
    首次授权通过回调地址中的code获取access_token
    :param app_id: 应用ID
    :param app_secret: 应用密钥
    :param code: 授权码
    :param grant_type: 授权类型，默认为"code"
    :return: 返回包含access_token的JSON响应
    """
    url = "https://openapi.kwaixiaodian.com/oauth2/access_token"
    params = {
        "app_id": app_id,
        "app_secret": app_secret,
        "code": code,
        "grant_type": grant_type
    }
    response = httpx.get(url, params=params)
    return response.json()

def refresh_access_token(app_id, app_secret, refresh_token, grant_type="refresh_token"):
    """
    刷新access_token
    :param app_id: 应用ID
    :param app_secret: 应用密钥
    :param refresh_token: 刷新令牌
    :param grant_type: 授权类型，默认为"refresh_token"
    :return: 返回包含新的access_token的JSON响应
    """
    url = "https://openapi.kwaixiaodian.com/oauth2/refresh_token"
    data = {
        "app_id": app_id,
        "app_secret": app_secret,
        "refresh_token": refresh_token,
        "grant_type": grant_type
    }
    response = httpx.post(url, data=data)
    return response.json()


if __name__ == "__main__":
    pass
