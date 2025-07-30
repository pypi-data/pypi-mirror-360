from pydantic import BaseModel, Field

class baseAppInfoSchema(BaseModel):
    """
    Base schema for all fund-related requests.
    """
    app_key: str = Field(default=None, description="Application key")
    secret: str = Field(default=None, description="Secret key")
    sign_secret: str = Field(default=None, description="Signature secret")