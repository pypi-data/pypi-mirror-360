from pydantic import BaseModel

# 登录响应模型
class LoginResponse(BaseModel):
    token: str