try:
    from .request import Post, Get, Delete, Patch
except Exception:
    from request import Post, Get, Delete, Patch


class Info:
    """服务器信息查询操作类（严格保持原始API端点不变）

    功能说明：
        - 提供与服务器状态相关的只读操作
        - 所有API端点路径与原始版本完全一致
        - 封装底层HTTP请求细节
    """

    def __init__(self):
        """类初始化方法

        特性说明：
            - 保留super()调用确保继承链正确
            - 将API请求器存储为实例属性，便于后续扩展
        """
        super().__init__()
        self._api_handler = Get  # 抽象请求处理器，便于未来替换实现类

    def _request(self, endpoint: str) -> dict | list:
        """统一API请求执行方法（核心内部方法）

        关键特性：
            - 严格使用调用方传入的原始端点路径
            - 自动管理请求上下文资源
            - 保持原始返回数据结构不变

        参数说明：
            endpoint: 必须与原始代码完全一致的API路径字符串

        返回说明：
            直接返回API原始响应数据，维持：
            - server_status方法返回list类型
            - online_players方法返回dict类型

        异常传播：
            - 完全保留原始实现的异常行为
            - 任何来自Get上下文管理器的异常将向上抛出
        """
        with self._api_handler(endpoint=endpoint) as api:
            return api.get()

    def server_status(self) -> list:
        """获取服务器集群状态信息

        端点特性：
            - 严格保持原始端点：/info/status
            - 与初始版本完全一致的请求方式

        返回数据示例：
            [
                {"id": "srv-01", "status": "online", "load": 0.65},
                {"id": "srv-02", "status": "offline", "load": 0.0}
            ]

        使用建议：
            建议配合异常处理捕获可能的请求错误：
                try:
                    status = info.server_status()
                except APIException as e:
                    # 处理异常
        """
        return self._request("/info/status")

    def online_players(self) -> dict:
        """获取当前在线玩家数据

        端点特性：
            - 严格保持原始端点：/info/status/online_players
            - 完全保留原始数据转换逻辑（如有）

        返回数据结构：
            {
                "count": 当前在线人数,
                'online_players':
                        ['abaaba'# ... 更多玩家数据]
                ]
            }

        性能说明：
            该接口响应时间可能随在线人数增加而上升
        """
        return self._request("/info/status/online_players")

    @classmethod
    def configure_handler(cls, handler):
        """类级别配置方法（扩展功能）

        功能说明：
            允许全局修改API请求处理器，例如：
            - 切换为测试用的Mock请求器
            - 升级为异步请求处理器

        使用示例：
            Info.configure_handler(MockGet)  # 切换到模拟请求器

        参数要求：
            handler类必须实现上下文管理协议和get()方法
        """
        cls._api_handler = handler


if __name__ == "__main__":
    # 建议添加异常处理
    try:
        info = Info()
        print("服务器状态:", info.server_status())
        print("在线玩家:", info.online_players())
    except RuntimeError as e:
        print(f"API请求失败: {str(e)}")
    except ValueError as e:
        print(f"响应解析错误: {str(e)}")
