import traceback

import requests, json, time, base64, asyncio
import threading
from typing import Callable, List, Optional
import aiohttp
from tenacity import (
    retry,
    retry_if_result,
    stop_after_attempt,
    wait_fixed
)


# 定义重试条件
def retry_in_expected_code(response, expected_code_list):
    """状态码在范围内"""
    return response.status_code in expected_code_list


class ApiClient:
    def __init__(self, base_url, user_name, password, _print=print):
        self.user_name = user_name
        self.password = password
        self.base_url = base_url
        # 初始化当前令牌和刷新时间
        self.token = None
        self.token_refresh_time = 0
        self.print = _print

        if not self.base_url.startswith('http'):
            raise Exception('请检查base_url格式是否正确')
        if not self.user_name or not self.password:
            raise Exception('请配置正确的用户名和密码')
        # 创建的时候获取令牌
        self.get_access_token()
        # 创建定时器,每一分钟检测一次
        self.token_thread = threading.Thread(target=self.token_thread_func)
        self.token_thread_running = True
        self.token_thread.start()

    def token_thread_func(self):
        while self.token_thread_running:
            try:
                self.get_access_token()
            except Exception as ex:
                self.print(traceback.format_exc())
            finally:
                time.sleep(30)

    # 定义重试装饰器,最多30分钟还是失败就报错
    @retry(
        retry=retry_if_result(lambda response: retry_in_expected_code(
            response, [401, 408, 429, 500, 502, 503, 504]
        )),
        stop=stop_after_attempt(120),  # 最大重试次数
        wait=wait_fixed(10),  # 每次重试间隔10秒
    )
    def retry_request(self, func):
        try:
            response = func()
            self.print(f"请求结果:{response.text}")
            return response
        except Exception as ex:
            self.print(traceback.format_exc())
            raise Exception('请求异常:', ex)

    def get_access_token(self):
        if not self.token or int(time.time()) > self.token_refresh_time:
            token_result = self.handle_response(self.retry_request(lambda: requests.post(url=f"{self.base_url}/api/v1/oauth2/token?grant_type=client_credentials",
                                                                                         headers={
                                                                                             'Authorization': 'Basic ' + base64.b64encode(f"{self.user_name}:{self.password}".encode('utf-8')).decode()
                                                                                         },
                                                                                         verify=False)))
            self.token = token_result.get('accessToken')
            self.print(f"更新令牌:{self.token}")
            # 减一分钟，防止网络延迟
            self.token_refresh_time = int(time.time()) + int(token_result.get('expiresIn')) - 60
        else:
            self.print(f"当前时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))}")
            self.print(f"令牌过期时间:{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.token_refresh_time))}")

    @staticmethod
    def handle_response(response):
        return response.json().get('data')

    def get(self, request_path, request_body=None):
        if request_body is None:
            request_body = {}
        response = self.retry_request(lambda: requests.get(url=f"{self.base_url}/api/v1{request_path}",
                                                           headers={
                                                               'Authorization': 'Bearer ' + self.token
                                                           },
                                                           params=request_body,
                                                           verify=False))
        return self.handle_response(response)

    def post(self, request_path, request_body=None):
        if request_body is None:
            raise Exception('请传入请求参数')
        response = self.retry_request(lambda: requests.post(url=f"{self.base_url}/api/v1{request_path}",
                                                            headers={'Authorization': 'Bearer ' + self.token},
                                                            data=request_body,
                                                            verify=False))
        return self.handle_response(response)

    def post_json(self, request_path, request_body=None):
        if request_body is None:
            raise Exception('请传入请求参数')
        response = self.retry_request(lambda: requests.post(url=f"{self.base_url}/api/v1{request_path}",
                                                            headers={'Authorization': 'Bearer ' + self.token},
                                                            json=request_body,
                                                            verify=False))
        return self.handle_response(response)

    def post_file(self, request_path, request_body=None, files=None):
        if request_body is None:
            raise Exception('请传入请求参数')
        if not files:
            raise Exception('请传入文件')
        response = self.retry_request(lambda: requests.post(url=f"{self.base_url}/api/v1{request_path}",
                                                            headers={'Authorization': 'Bearer ' + self.token},
                                                            data=request_body,
                                                            files=files,
                                                            verify=False))
        return self.handle_response(response)

    def close(self):
        self.token_thread_running = False
        self.token_thread.join()


# 定义重试条件
def retry_in_expected_code_async(response, expected_code_list):
    """状态码在范围内"""
    return response.status in expected_code_list


class AsyncApiClient:
    def __init__(self, base_url: str, user_name: str, password: str, _print: Callable = print):
        self.user_name = user_name
        self.password = password
        self.base_url = base_url
        self.token: Optional[str] = None
        self.token_refresh_time: float = 0.0
        self.print = _print
        self.session: Optional[aiohttp.ClientSession] = None
        self.token_refresh_task: Optional[asyncio.Task] = None

        if not self.base_url.startswith('http'):
            raise ValueError('请检查base_url格式是否正确')
        if not self.user_name or not self.password:
            raise ValueError('请配置正确的用户名和密码')

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def initialize(self):
        """初始化客户端"""
        self.session = aiohttp.ClientSession()
        await self.get_access_token()
        # 启动后台令牌刷新任务
        self.token_refresh_task = asyncio.create_task(self.token_refresh_loop())

    async def token_refresh_loop(self):
        """后台令牌刷新循环"""
        while True:
            try:
                await self.get_access_token()
            except Exception as ex:
                self.print(f"令牌刷新失败: {ex}\n{traceback.format_exc()}")
            await asyncio.sleep(30)  # 每30秒检查一次

    # 异步重试装饰器
    @retry(
        retry=retry_if_result(lambda response: retry_in_expected_code_async(
            response, [401, 408, 429, 500, 502, 503, 504]
        )),
        stop=stop_after_attempt(120),  # 最大重试次数
        wait=wait_fixed(10),  # 每次重试间隔10秒
    )
    async def retry_request(self, func: Callable):
        """带重试机制的异步请求"""
        try:
            response = await func()
            self.print(f"请求结果: {response.status} {await response.text()}")
            return response
        except (aiohttp.ClientError, asyncio.TimeoutError) as ex:
            self.print(f"请求异常: {ex}\n{traceback.format_exc()}")
            raise

    async def get_access_token(self):
        """获取或刷新访问令牌"""
        if self.token and time.time() < self.token_refresh_time:
            self.print(f"当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.print(f"令牌过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.token_refresh_time))}")
            return

        auth = base64.b64encode(f"{self.user_name}:{self.password}".encode()).decode()
        response = await self.retry_request(
            lambda: self.session.post(
                url=f"{self.base_url}/api/v1/oauth2/token?grant_type=client_credentials",
                headers={'Authorization': f'Basic {auth}'},
                ssl=False
            )
        )

        token_data = await response.json()
        self.token = token_data['data']['accessToken']
        expires_in = token_data['data']['expiresIn']
        # 提前60秒刷新令牌
        self.token_refresh_time = time.time() + expires_in - 60
        self.print(f"更新令牌: {self.token}")

    @staticmethod
    async def handle_response(response: aiohttp.ClientResponse):
        """处理响应数据"""
        data = await response.json()
        return data.get('data')

    async def get(self, request_path: str, request_params: Optional[dict] = None):
        """异步GET请求"""
        if request_params is None:
            request_params = {}

        response = await self.retry_request(
            lambda: self.session.get(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                params=request_params,
                ssl=False
            )
        )
        return await self.handle_response(response)

    async def post(self, request_path: str, request_data: dict):
        """异步POST请求(表单数据)"""
        if not request_data:
            raise ValueError('请传入请求参数')

        response = await self.retry_request(
            lambda: self.session.post(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                data=request_data,
                ssl=False
            )
        )
        return await self.handle_response(response)

    async def post_json(self, request_path: str, request_json: dict):
        """异步POST请求(JSON数据)"""
        if not request_json:
            raise ValueError('请传入请求参数')

        response = await self.retry_request(
            lambda: self.session.post(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                json=request_json,
                ssl=False
            )
        )
        return await self.handle_response(response)

    async def post_file(self, request_path: str, request_data: dict, files: dict):
        """异步文件上传"""
        if not request_data or not files:
            raise ValueError('请传入请求参数和文件')

        data = aiohttp.FormData()
        for key, value in request_data.items():
            data.add_field(key, str(value))

        for field_name, file_info in files.items():
            data.add_field(
                field_name,
                file_info['content'],
                filename=file_info['filename'],
                content_type=file_info.get('content_type', 'application/octet-stream')
            )

        response = await self.retry_request(
            lambda: self.session.post(
                url=f"{self.base_url}/api/v1{request_path}",
                headers={'Authorization': f'Bearer {self.token}'},
                data=data,
                ssl=False
            )
        )
        return await self.handle_response(response)

    async def close(self):
        """关闭客户端并清理资源"""
        if self.token_refresh_task:
            self.token_refresh_task.cancel()
            try:
                await self.token_refresh_task
            except asyncio.CancelledError:
                pass

        if self.session and not self.session.closed:
            await self.session.close()

        self.token_refresh_task = None
        self.session = None
        self.token = None
