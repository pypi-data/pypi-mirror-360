import atexit
import sys
import asyncio
import aiohttp
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_random

g_headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyX2lkIjotMSwidXNlcl9uYW1lIjoiXHU1ZTk0XHU3NTI4XHU0ZTJkXHU1ZmMzQ2xpZW50In0.'
}

"""
cls._conn = aiohttp.TCPConnector(
        limit=50,  # 最大连接数
        ssl=False,  # 禁用SSL验证（按需开启）
        force_close=True,  # 保持连接活跃
        enable_cleanup_closed=True  # 自动清理关闭的连接 
    )
# 由于网络上有重名，没有连接。如果加入域，请转到“控制面板”中的“系统”更改计算机名，然后重试。如果加入工作组，请选择其他工作组名。
有可能是 
force_close=True,  # 保持连接活跃
enable_cleanup_closed=True  # 自动清理关闭的连接 
照成的
"""


class HttpError(Exception):
    code = 0
    message = ""
    headers = None

    def __init__(
            self,
            *,
            code: Optional[int] = None,
            message: str = "",
            headers: Optional[dict] = None,
    ) -> None:
        if code is not None:
            self.code = code
        self.headers = headers
        self.message = message

    def __str__(self) -> str:
        return f"code: {self.code}, message:{self.message}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: code={self.code}, message={self.message!r}>"


def on_retry_error(retry_state):
    # 最后抛错后调用
    original_exc = retry_state.outcome.exception()
    print(f"[HTTP 请求重试所有重试失败.] 错误消息{original_exc}")

    raise HttpError(code=getattr(original_exc, 'code', 455),
                    message=f"错误消息:{str(original_exc)}") from original_exc


def on_retry(retry_state):
    # 每次抛错进入该函数打印消息
    print(
        f"[HTTP 请求重试]"
        f"当前重试 : 第 {retry_state.attempt_number} 次"
        f"睡眠时间 : {retry_state.next_action.sleep:.2f} 秒"
        f"\n异常原因 : {retry_state.outcome.exception()}"
    )


class ApiNetUtils:
    """
    HTTP请求工具类（异步版），提供GET/POST/PATCH请求方法
    特性：
    1. 自动复用TCP连接池
    2. 自动重试机制（通过async_retry装饰器）
    3. 进程退出时自动清理资源
    4. 线程安全的延迟初始化
    """

    # 类属性使用Optional类型注解，初始化为None实现延迟初始化
    _conn: Optional[aiohttp.TCPConnector] = None
    _session: Optional[aiohttp.ClientSession] = None
    _close_registered: bool = False  # 确保清理函数只注册一次

    @classmethod
    async def _get_connector(cls) -> aiohttp.TCPConnector:
        """
        获取TCP连接器（延迟初始化）
        解决模块加载时没有事件循环的问题
        """
        if cls._conn is None or cls._conn.closed or cls.is_loop_closed(cls._session):
            # 只有在首次使用时才创建连接器
            cls._conn = aiohttp.TCPConnector(
                limit=50,  # 最大连接数
                ssl=False,  # 禁用SSL验证（按需开启）
                force_close=True,  # 保持连接活跃
                # enable_cleanup_closed=True,  # 自动清理关闭的连接 #
                # keepalive_timeout=4.99  # 比服务器的5s 小一点
            )
        return cls._conn

    @classmethod
    async def _get_session(cls) -> aiohttp.ClientSession:
        """
        获取共享会话（线程安全的延迟初始化）
        包含自动注册清理机制
        """
        if cls._session is None or cls._session.closed or cls.is_loop_closed(cls._session):
            if cls._session:
                await cls.close()
            # 获取连接器（会自动初始化）
            connector = await cls._get_connector()

            # 强制获取新的事件循环
            loop = asyncio.get_event_loop()

            # 创建新会话
            cls._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=30),  # 默认30秒超时
                loop=loop)  # 显式指定事件循环

            # # 注册退出时的清理钩子
            cls._register_cleanup()

        return cls._session

    @staticmethod
    def is_loop_closed(session: aiohttp.ClientSession) -> bool:
        """
        检查会话绑定的事件循环是否已关闭
        """
        loop = session._loop  # 获取会话绑定的事件循环
        if loop.is_closed():
            # print("Event loop is closed")
            return True
        # print("Event loop not is closed")
        return False

    @classmethod
    def _register_cleanup(cls):
        """
        注册进程退出时的资源清理函数
        包含正常退出和异常退出两种情况
        """
        if not cls._close_registered:
            # 1. 正常退出处理
            atexit.register(lambda: asyncio.run(cls.close()))

            # 2. 异常退出处理
            original_excepthook = sys.excepthook

            def custom_excepthook(exctype, value, traceback):
                """自定义异常钩子，确保资源被清理"""
                # 先执行原始异常处理（打印堆栈等）
                original_excepthook(exctype, value, traceback)
                # 然后执行资源清理
                try:
                    asyncio.run(cls.close())
                except RuntimeError:
                    # 如果已经没有事件循环，则同步执行
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(cls.close())
                    loop.close()

            sys.excepthook = custom_excepthook
            cls._close_registered = True

    @classmethod
    async def close(cls):
        """
        安全关闭所有网络资源
        会自动在程序退出时调用，也可手动调用
        """
        if cls._session and not cls._session.closed:
            await cls._session.close()
            cls._session = None

        if cls._conn and not cls._conn.closed:
            await cls._conn.close()
            cls._conn = None

        # print("[ApiNetUtils] 网络资源已安全释放")

    # -------------------- 公共API方法 -------------------- #

    @classmethod
    @retry(stop=stop_after_attempt(4),  # 本质上执行4次 但重试3次
           wait=wait_random(min=5, max=15),
           before_sleep=on_retry,  # 每次抛错后使用
           retry_error_callback=on_retry_error,
           reraise=True)
    async def fetch_get(cls, url: str, headers=None, params=None):
        """
        GET请求封装
        :param url: 请求URL
        :param headers: 可选请求头（默认使用全局g_headers）
        :param params: 查询参数（字典）
        :return: 解析后的JSON数据
        :raises HttpError: 当状态码非200时抛出
        """
        headers = headers or g_headers
        session = await cls._get_session()

        async with session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                error_text = await response.text()
                raise HttpError(
                    code=response.status,
                    message=f"请求失败: url={url}, status={response.status}, 错误详情={error_text}"
                )
            return await response.json()

    @classmethod
    @retry(stop=stop_after_attempt(4),
           wait=wait_random(min=5, max=15),
           before_sleep=on_retry,  # 每次抛错后使用
           retry_error_callback=on_retry_error,
           reraise=True)
    async def fetch_post(cls, url: str, payload: dict, headers=None):
        """
        POST请求封装（JSON格式）
        """
        headers = headers or g_headers
        session = await cls._get_session()

        async with session.post(url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise HttpError(
                    code=response.status,
                    message=f"请求失败: url={url}, status={response.status}, 错误详情={error_text}"
                )
            return await response.json()

    @classmethod
    @retry(stop=stop_after_attempt(4),
           wait=wait_random(min=5, max=15),
           before_sleep=on_retry,  # 每次抛错后使用
           retry_error_callback=on_retry_error,
           reraise=True)
    async def fetch_patch(cls, url: str, payload: dict, headers=None):
        """
        PATCH请求封装（JSON格式）
        """
        headers = headers or g_headers
        session = await cls._get_session()

        async with session.patch(url, json=payload, headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                raise HttpError(
                    code=response.status,
                    message=f"请求失败: url={url}, status={response.status}, 错误详情={error_text}"
                )
            return await response.json()

    @classmethod
    async def __aenter__(cls):
        """支持async with语法"""
        await cls._get_session()
        return cls

    @classmethod
    async def __aexit__(cls, exc_type, exc, tb):
        """async with退出时自动关闭"""
        await cls.close()
