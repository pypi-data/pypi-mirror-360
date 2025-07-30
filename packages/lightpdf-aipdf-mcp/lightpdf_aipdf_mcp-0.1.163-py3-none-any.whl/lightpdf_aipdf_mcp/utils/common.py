"""通用工具模块"""
import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from fastmcp import Context
from typing import List, Optional, Dict, Any, Tuple, TypeVar, Callable
from functools import wraps
import urllib.parse
import httpx

T = TypeVar('T', bound='BaseResult')

@dataclass
class BaseResult:
    """基础结果数据类"""
    success: bool = False
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None
    original_name: Optional[str] = None
    task_id: Optional[str] = None

def require_api_key(func: Callable) -> Callable:
    """装饰器：自动检查API密钥并处理错误
    
    使用方法：
    @require_api_key
    async def some_method(self, file_path: str, ...) -> SomeResult:
        # 方法实现
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # 检查是否有api_key属性
        if not hasattr(self, 'api_key') or not self.api_key:
            # 记录错误
            if hasattr(self, 'logger'):
                await self.logger.error("未找到API_KEY。请在客户端配置API_KEY环境变量。")
            
            # 尝试从方法参数中获取必要的信息
            file_path = None
            original_name = None
            
            # 从位置参数中查找
            if args:
                file_path = args[0] if len(args) > 0 and isinstance(args[0], str) else None
            
            # 从关键字参数中查找
            file_path = kwargs.get('file_path', file_path)
            original_name = kwargs.get('original_name')
            
            # 获取返回类型注解
            return_type = func.__annotations__.get('return')
            
            # 如果有返回类型且可以实例化
            if return_type:
                try:
                    # 动态创建结果对象
                    return return_type(
                        success=False,
                        file_path=file_path,
                        error_message="未找到API_KEY",
                        original_name=original_name
                    )
                except:
                    pass
            
            # 如果无法创建特定类型，使用基础结果类
            return BaseResult(
                success=False,
                file_path=file_path,
                error_message="未找到API_KEY",
                original_name=original_name
            )
        
        # API密钥存在，执行原方法
        return await func(self, *args, **kwargs)
    
    return wrapper

class Logger:
    """日志记录器类"""
    def __init__(self, context: Context, collect_info: bool = True):
        self.context = context
        self.collect_info = collect_info
        self._info_log = []
        self._debug = os.getenv("DEBUG")

    async def log(self, level: str, message: str, add_to_result: bool = True):
        """记录日志消息"""
        if self.collect_info and add_to_result:
            self._info_log.append(message)
            
        # DEBUG模式下打印到stderr
        if self._debug:
            print(f"[{level.upper()}] {message}", file=sys.stderr)
        
        # 发送到FastMCP Context
        if level.lower() == "error":
            await self.context.error(message)
        elif level.lower() == "warning":
            await self.context.info(f"⚠️ {message}")
        elif level.lower() == "debug":
            if self._debug:
                await self.context.info(f"🐛 {message}")
        else:
            await self.context.info(message)
    
    async def error(self, message: str, error_class=RuntimeError):
        """记录错误并引发异常"""
        await self.log("error", message)
        raise error_class(message)
        
    def get_result_info(self) -> List[str]:
        """获取收集的信息日志"""
        return self._info_log

class FileHandler:
    """文件处理工具类"""
    def __init__(self, logger: Logger):
        self.logger = logger

    @staticmethod
    def is_url(path: str) -> bool:
        """检查路径是否为URL"""
        return path.startswith(("http://", "https://", "oss://"))
        
    @staticmethod
    def is_oss_id(path: str) -> bool:
        """检查路径是否为OSS ID"""
        return path.startswith("oss_id://")

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """获取文件扩展名（小写）"""
        if "?" in file_path:  # 处理URL中的查询参数
            file_path = file_path.split("?")[0]
        return os.path.splitext(file_path)[1].lower()
        
    @staticmethod
    def get_input_format(file_path: str):
        """根据文件路径获取输入格式
        
        此方法需要导入InputFormat和INPUT_EXTENSIONS，
        但为避免循环导入，由调用者提供转换逻辑
        """
        ext = FileHandler.get_file_extension(file_path)
        return ext
        
    @staticmethod
    def get_available_output_formats(input_format):
        """获取指定输入格式支持的输出格式
        
        此方法需要导入FORMAT_CONVERSION_MAP，
        但为避免循环导入，由调用者提供转换逻辑
        """
        # 实际实现在converter.py
        return {}

    async def validate_file_exists(self, file_path: str) -> bool:
        """验证文件是否存在
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 文件是否存在
        """
        is_url = self.is_url(file_path)
        is_oss = self.is_oss_id(file_path)
        
        # 对于URL或OSS路径，假设它们是有效的
        if is_url or is_oss:
            return True
            
        if not os.path.exists(file_path):
            await self.logger.error(f"文件不存在：{file_path}", FileNotFoundError)
            return False
            
        return True

class BaseApiClient:
    """API客户端基类"""
    def __init__(self, logger: Logger, file_handler: FileHandler):
        self.logger = logger
        self.file_handler = file_handler
        self.api_key = os.getenv("API_KEY")
        self.api_endpoint = os.getenv("API_ENDPOINT", "techsz.aoscdn.com/api")
        # 子类必须设置api_base_url
        self.api_base_url = None

    async def _create_task(self, client: httpx.AsyncClient, file_path: str, data: dict, response_action: str = "创建任务") -> str:
        """通用任务创建方法，支持OSS、URL、本地文件三种情况
        Args:
            client: HTTP客户端
            file_path: 文件路径
            data: API参数字典
            response_action: 日志/错误前缀
        Returns:
            str: 任务ID
        """
        await self.logger.log("info", f"正在提交{response_action}...{data}")
        headers = {"X-API-KEY": self.api_key}
        # 检查是否为OSS路径
        if self.file_handler.is_oss_id(file_path):
            data = data.copy()
            data["resource_id"] = file_path.split("oss_id://")[1]
            headers["Content-Type"] = "application/json"
            response = await client.post(
                self.api_base_url,
                json=data,
                headers=headers
            )
        elif self.file_handler.is_url(file_path):
            file_path_mod = file_path
            if isinstance(file_path, str) and "arxiv.org/pdf/" in file_path:
                from urllib.parse import urlparse, urlunparse
                url_obj = urlparse(file_path)
                if not url_obj.path.endswith(".pdf"):
                    new_path = url_obj.path + ".pdf"
                    file_path_mod = urlunparse(url_obj._replace(path=new_path))
            data = data.copy()
            data["url"] = file_path_mod
            headers["Content-Type"] = "application/json"
            response = await client.post(
                self.api_base_url,
                json=data,
                headers=headers
            )
        else:
            with open(file_path, "rb") as f:
                files = {"file": f}
                response = await client.post(
                    self.api_base_url,
                    files=files,
                    data=data,
                    headers=headers
                )
        return await self._handle_api_response(response, response_action)

    async def _wait_for_task(self, client: httpx.AsyncClient, task_id: str, operation_type: str = "处理", is_raw: bool = False) -> str | dict:
        """等待任务完成并返回下载链接
        
        Args:
            client: HTTP客户端
            task_id: 任务ID
            operation_type: 操作类型描述，用于日志，默认为"处理"
            
        Returns:
            str: 下载链接
            
        Raises:
            RuntimeError: 如果任务失败或超时
        """
        headers = {"X-API-KEY": self.api_key}
        MAX_ATTEMPTS = 120
        
        for attempt in range(MAX_ATTEMPTS):
            await asyncio.sleep(5)
            
            status_response = await client.get(
                f"{self.api_base_url}/{task_id}",
                headers=headers
            )
            
            if status_response.status_code != 200:
                await self.logger.log("warning", f"获取任务状态失败。状态码: {status_response.status_code}")
                continue
            
            status_result = status_response.json().get("data", {})
            state = status_result.get("state")
            progress = status_result.get("progress", 0)
            
            if state == 1:  # 完成
                if is_raw:
                    return status_result
                
                download_url = status_result.get("file")
                if not download_url:
                    file_hash = status_result.get("file_hash")
                    if file_hash:
                        return file_hash
                    await self.logger.error(f"任务完成但未找到下载链接。任务状态：{json.dumps(status_result, ensure_ascii=False)}")
                return download_url
            elif state < 0:  # 失败
                await self.logger.error(f"任务失败: {json.dumps(status_result, ensure_ascii=False)}")
            else:  # 进行中
                await self.logger.log("debug", f"{operation_type}进度: {progress}%", add_to_result=False)
        
        await self.logger.error(f"超过最大尝试次数（{MAX_ATTEMPTS}），任务未完成")

    async def _handle_api_response(self, response: httpx.Response, error_prefix: str) -> str:
        """处理API响应并提取任务ID
        
        Args:
            response: API响应
            error_prefix: 错误消息前缀
            
        Returns:
            str: 任务ID
            
        Raises:
            RuntimeError: 如果响应无效或任务ID缺失
        """
        if response.status_code != 200:
            await self.logger.error(f"{error_prefix}失败。状态码: {response.status_code}\n响应: {response.text}")
        
        result = response.json()
        if "data" not in result or "task_id" not in result["data"]:
            await self.logger.error(f"无法获取任务ID。API响应：{json.dumps(result, ensure_ascii=False)}")
        
        await self.logger.log("debug", f"API响应：{json.dumps(result, ensure_ascii=False)}")
        return result["data"]["task_id"]