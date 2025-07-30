from typing import Dict, Any

try:
    from .request import Post, Get, Delete, Patch
except Exception:
    from request import Post, Get, Delete, Patch


class EaCyVerGoneAPIClient:
    """
    EaCyVerGoneAPI SDK 客户端

    提供对Mzmc API的访问接口，支持版本查询和资源链接获取功能
    """

    def __init__(self, base_url: str = "https://mzmc-api.647382.xyz"):
        """
        初始化客户端

        Args:
            base_url: API基础地址，默认使用官方地址
        """
        self.base_url = base_url
        self.headers = {"User-Agent": "MzmcAPISDK/1.0"}

    def get_version(self, product: str) -> Dict[str, Any]:
        """
        获取指定产品的最新版本信息

        Args:
            product: 产品名称

        Returns:
            包含版本信息的字典，格式为：
            {
                "status": "200",
                "content": {
                    "remote_version": "版本号",
                    "link": "下载链接",
                    "body": "版本说明"
                }
            }

        Raises:
            httpx.HTTPStatusError: 当API返回非200状态码时抛出
        """
        url = f"/api/v1/mzmc/version/{product}"
        with Get(base_url=self.base_url, endpoint=url) as api:
            return api.get(header=self.headers)

    def get_launcher_link(self) -> Dict[str, Any]:
        """
        获取启动器下载链接

        Returns:
            包含下载链接的字典，格式为：
            {
                "status": "200",
                "content": {
                    "url": "下载链接"
                }
            }

        Raises:
            httpx.HTTPStatusError: 当API返回非200状态码时抛出
        """
        url = "/api/v1/mzmc/link/launcher"
        with Get(base_url=self.base_url, endpoint=url) as api:
            return api.get(header=self.headers)


if __name__ == "__main__":
    client = EaCyVerGoneAPIClient()
    print(client.get_version("MianzhongMinecraftLoader"))
    print(client.get_launcher_link())
