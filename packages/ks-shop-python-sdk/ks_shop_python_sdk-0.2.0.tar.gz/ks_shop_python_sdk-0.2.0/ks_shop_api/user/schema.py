# -*- coding: utf-8 -*-
from pydantic import BaseModel, Field
from typing import Optional, List


class OpenUserFansCheckSchema(BaseModel):
    fromOpenId: Optional[str] = Field(default=None, description="用户的openId，同一个用户在同一个开发者主体下返回的openId是一致的，可通过open.user.info.get获取")


class OpenUserInfoGetSchema(BaseModel):
    pass


class OpenUserSellerGetSchema(BaseModel):
    pass



















