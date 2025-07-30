import sys
from pathlib import Path
# 将项目根目录添加到 sys.path
root_dir = Path(__file__).parent.parent  # 根据文件位置调整层级
sys.path.insert(0, str(root_dir))

from ks_shop_api.schema import baseAppInfoSchema
from pydantic import BaseModel
from ks_shop_api.base import RestApi


def base_request(req: RestApi, params: dict | BaseModel = {}):
    """
    Test function for RestApi requests.
    """
    access_token = 'ChFvYXV0aC5hY2Nlc3NUb2tlbhJwcZLBCMATtem3aKCFHyM_u0S2N2N4jhJQEzxguz4pg17piwSeJS6twMsYTcYflZc_VxA_1Haf83nOnMbM_dIKGkARHUaOhPza6tI3XOuAN58h3MPi4ms9Npnc_MDhYYzHI3MoLNTxHEWcrxUPZ5yEOhoSHg1tDvxyRRCow8UkANziUyedIiAVBZ8wZ3C_ApcYUnCaA7YmGM34fRb0gCIAxthGfNUuAygFMAE'
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


def base_dict(req: RestApi, params: dict | BaseModel = {}):
    access_token = 'ChFvYXV0aC5hY2Nlc3NUb2tlbhJwcZLBCMATtem3aKCFHyM_u0S2N2N4jhJQEzxguz4pg17piwSeJS6twMsYTcYflZc_VxA_1Haf83nOnMbM_dIKGkARHUaOhPza6tI3XOuAN58h3MPi4ms9Npnc_MDhYYzHI3MoLNTxHEWcrxUPZ5yEOhoSHg1tDvxyRRCow8UkANziUyedIiAVBZ8wZ3C_ApcYUnCaA7YmGM34fRb0gCIAxthGfNUuAygFMAE'
    app_info = {
        "app_key": "ks653021946718290428",
        "secret": "ITeSl4qooSGxrdTMQ",
        "sign_secret": "dc90166e66aa4a4a5921bf0e2941a4fe"
    }
    req_obj: RestApi = req(**app_info)
    try:
        response = req_obj.getResponse(access_token, params=params)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
