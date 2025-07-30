try:
    from .request import Post, Get, Delete, Patch
except Exception:
    from request import Post, Get, Delete, Patch
from hashlib import sha256

from loguru import logger


class AuthClient:
    """统一认证客户端"""

    _token = None
    _base_url = "https://api.mzmc.top"
    _headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MzmcOS; +https://mzmc.top) MzmcOS/Loader",
        "Content-Type": "application/json"
    }

    def __init__(self):
        pass

    def login(self, **credentials) -> dict:
        """智能登录方法
        :param credentials: {"email": "邮箱","username": "用户名","password": "密码"}
        """
        # 自动检测凭证类型
        if 'email' in credentials:
            auth_type = 'email'
            required = ['email', 'password']
            payload = {
                "email": credentials[auth_type].strip(),
                "password": sha256(credentials['password'].encode()).hexdigest()
            }
        elif 'username' in credentials:
            auth_type = 'username'
            required = ['username', 'password']
            # 构建请求载荷
            payload = {
                "username": credentials[auth_type].strip(),
                "password": sha256(credentials['password'].encode()).hexdigest()
            }
        else:
            raise ValueError("无效的凭证类型，请提供username或email")

        if not all(credentials.get(k) for k in required):
            raise ValueError(f"缺少必要参数: {required}")


        # 发送请求
        with Post(endpoint="/user/auth/login", base_url=self._base_url) as api:
            try:
                result = api.post(json_data=payload)
            except:
                return {"is_login": False}
            self._token = result['data']['access_token']
            logger.trace(f"登录；result:{result}")
            return result

    def logout(self) -> bool:
        """一键登出"""
        if not self._token:
            return False

        with Post(endpoint="/user/auth/logout", base_url=self._base_url) as api:
            try:
                api.post(headers={"Authorization": f"Bearer {self._token}"})
                self._token = None
                return True
            except:
                return False

    def check_login(self) -> dict:
        """验证登录状态"""
        if not self._token:
            return {"is_login": False}

        with Post(endpoint="/user/auth/check", base_url=self._base_url) as api:
            return api.post(json_data={"Authorization": f"Bearer {self._token}"})

    def bind(self, qq) -> dict:
        """绑定qq与玩家
        :param qq QQ号
        """
        if not self._token:
            return {"is_login": False}
        payload={
            "qq_id": qq,
            "token": self._token
        }
        with Post(endpoint="/user/bind/qq", base_url=self._base_url) as api:
            result = api.post(json_data=payload)
            logger.trace(f"绑定qq与玩家；result:{result}")
            if not (200 <= result['code'] <= 299):
                logger.error(f"绑定qq与玩家失败；result:{result}")
            return result

    def unbind(self) -> dict:
        """解绑qq与玩家
        """
        if not self._token:
            return {"is_login": False}
        payload={
            "token": self._token
        }
        with Delete(endpoint="/user/bind/qq", base_url=self._base_url) as api:
            result = api.delete(json_data=payload)
            logger.trace(f"取消绑定qq与玩家；result:{result}")
            return result

    def get_qq(self) -> dict:
        """获取qq绑定信息
        """
        if not self._token:
            return {"is_login": False}
        payload = {
            "token": self._token
        }
        with Get(endpoint="/user/bind/qq", base_url=self._base_url) as api:
            result = api.get(json_data=payload)
            logger.trace(f"获取qq绑定信息；result:{result}")
            return result