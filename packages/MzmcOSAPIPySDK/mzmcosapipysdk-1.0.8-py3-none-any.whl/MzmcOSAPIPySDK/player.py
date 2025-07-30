try:
    from .request import Post, Get, Delete, Patch
except Exception:
    from request import Post, Get, Delete, Patch


class Player:
    """玩家信息操作类，提供不同身份的角色查询接口

    特性说明：
        - 严格保持所有原始API端点路径不变
        - 区分普通用户接口和管理员接口
        - 自动处理授权凭证的传输
    """

    def __init__(self):
        """初始化玩家信息操作实例"""
        super().__init__()

    @staticmethod
    def _request(endpoint: str, access_token: str = None) -> dict:
        """内部统一请求方法（核心逻辑封装）

        参数说明：
            endpoint: 完整的API端点路径，必须与原始定义完全一致
            access_token: 可选的身份验证凭证

        返回说明：
            返回原始API响应数据的字典结构

        异常说明：
            可能抛出以下异常：
            - 401 Unauthorized: 当access_token无效或权限不足
            - 404 Not Found: 当查询的资源不存在
        """
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        with Get(endpoint=endpoint) as api:
            return api.get(header=headers)

    def profile(self, access_token: str = None) -> dict:
        """查询当前认证用户的档案信息（用户接口）

        端点说明：
            - 原始端点：/player/profile
            - 需要有效的access_token

        参数说明：
            access_token: 用户身份凭证，用于验证请求权限

        返回示例：
            {
		        "id": 2,
		        "username": "laobinghu",
		        "realname": "laobinghu",
		        "nickname": "laobinghu",
		        "email": "923190468@qq.com",
		        "is_logged": false
	        }

        使用场景：
            普通用户查看自己的个人信息
        """
        return self._request("/player/profile", access_token)

    def profile_by_id(self, access_token: str = None, uid: int = None) -> dict:
        """通过数字ID查询用户档案（管理员接口）

        端点说明：
            - 原始端点：/player/profile/id/{uid}
            - 需要管理员权限的access_token

        参数说明：
            access_token: 管理员身份凭证
            uid: 要查询的玩家数字ID

        返回示例：
            {
		        "id": 2,
		        "username": "laobinghu",
		        "realname": "laobinghu",
		        "nickname": "laobinghu",
		        "email": "923190468@qq.com",
		        "is_logged": false
	        }

        权限要求：
            调用者必须具有管理员权限
        """
        return self._request(f"/player/profile/id/{uid}", access_token)

    def profile_by_username(self, access_token: str = None, username: str = None) -> dict:
        """通过用户名查询用户档案（管理员接口）

        端点说明：
            - 原始端点：/player/profile/username/{username}
            - 需要管理员权限的access_token

        参数说明：
            access_token: 管理员身份凭证
            username: 要查询的玩家用户名（区分大小写）

        返回示例：
            {
		        "id": 2,
		        "username": "laobinghu",
		        "realname": "laobinghu",
		        "nickname": "laobinghu",
		        "email": "923190468@qq.com",
		        "is_logged": false
	        }

        特殊说明：
            用户名查询为精确匹配，不支持模糊搜索
        """
        return self._request(f"/player/profile/username/{username}", access_token)

    def profile_of_all(self, access_token: str = None) -> dict:
        """查询所有用户档案（超级管理员接口）

        端点说明：
            - 原始端点：/player/profile/all
            - 需要超级管理员权限的access_token

        参数说明：
            access_token: 超级管理员身份凭证

        返回示例：
            [
                {"id": 1,, "username": "user1", ...},
                ...

        安全警告：
            该接口返回敏感信息，应严格控制访问权限
        """
        return self._request("/player/profile/all", access_token)
