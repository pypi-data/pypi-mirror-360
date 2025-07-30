import httpx
import logging
import os
import json
import time
import asyncio
import uuid
from typing import Dict, Any, Optional, Union, List, Tuple, ClassVar
from dotenv import load_dotenv
from urllib.parse import urljoin

# 加载环境变量
load_dotenv()

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# 添加控制台处理器
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

class HiFlyAPIError(Exception):
    """飞影API错误异常类"""
    def __init__(self, code: int, message: str, request_id: str = None):
        self.code = code
        self.message = message
        self.request_id = request_id
        super().__init__(f"API Error {code}: {message} (Request ID: {request_id})")

class HiFlyClient:
    """飞影API客户端（单例模式）"""
    
    # 单例实例
    _instance: ClassVar[Optional["HiFlyClient"]] = None
    # 初始化标志
    _initialized: ClassVar[bool] = False
    # 请求缓存，用于去重
    _request_cache: ClassVar[Dict[str, Tuple[float, Any]]] = {}
    # 缓存过期时间（秒）
    _cache_ttl: ClassVar[float] = 1.0
    
    # 错误码映射
    ERROR_CODES = {
        11: "参数不正确",
        14: "找不到资源",
        1001: "正在生成中的作品数量达到上限",
        1002: "积分不足",
        1005: "开通会员",
        1006: "会员等级不够",
        1009: "高保真声音已售罄",
        1011: "声音与名人相似",
        1013: "高保真声音达到克隆数量上限",
        1015: "提交的作品数量达到上限",
        2003: "无效Token",
        2011: "文件大小超过限制",
        2012: "文件类型不支持",
        2013: "获取音频资源失败",
        2014: "获取视频资源失败",
        2015: "数字人克隆失败"
    }
    
    def __new__(cls, *args, **kwargs):
        """实现单例模式"""
        if cls._instance is None:
            cls._instance = super(HiFlyClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, api_token: str = None, base_url: str = None, timeout: int = 30, max_retries: int = 3, retry_delay: int = 1):
        """
        初始化飞影API客户端
        
        Args:
            api_token: API令牌，如果为None则从环境变量FLYWORKS_API_TOKEN获取
            base_url: API基础URL，如果为None则从环境变量FLYWORKS_API_BASE_URL获取，默认为https://hfw-api.hifly.cc/api/v2/hifly
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）
        """
        # 保存初始化参数，以便后续重新初始化
        self.api_token = api_token or os.getenv("FLYWORKS_API_TOKEN")
        if not self.api_token:
            raise ValueError("API令牌未提供，请设置FLYWORKS_API_TOKEN环境变量或在初始化时提供api_token参数")
        
        self.base_url = base_url or os.getenv("FLYWORKS_API_BASE_URL", "https://hfw-api.hifly.cc/api/v2/hifly")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # 如果是首次初始化或客户端不存在，则创建HTTP客户端
        if not hasattr(self, 'client') or self.client is None:
            self._create_client()
            logger.info(f"HiFlyClient initialized with base_url: {self.base_url}")
        
        # 标记为已初始化
        self.__class__._initialized = True
    
    def _create_client(self):
        """创建HTTP客户端"""
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        logger.info("Created new HTTP client")
    
    async def close(self):
        """关闭HTTP客户端"""
        if hasattr(self, 'client') and self.client is not None:
            await self.client.aclose()
            self.client = None
            logger.info("HTTP client closed")
    
    def _ensure_client(self):
        """确保客户端存在并可用"""
        if not hasattr(self, 'client') or self.client is None:
            logger.info("Client was closed, recreating...")
            self._create_client()
    
    def _get_cache_key(self, method: str, url: str, params: Dict[str, Any] = None, json_data: Dict[str, Any] = None) -> str:
        """生成请求缓存键"""
        cache_parts = [method, url]
        if params:
            cache_parts.append(json.dumps(params, sort_keys=True))
        if json_data:
            cache_parts.append(json.dumps(json_data, sort_keys=True))
        return ":".join(cache_parts)
    
    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """检查请求缓存"""
        if cache_key in self._request_cache:
            timestamp, response = self._request_cache[cache_key]
            # 检查缓存是否过期
            if time.time() - timestamp <= self._cache_ttl:
                logger.info(f"Using cached response for request: {cache_key}")
                return response
            # 缓存已过期，删除
            del self._request_cache[cache_key]
        return None
    
    def _update_cache(self, cache_key: str, response: Dict[str, Any]):
        """更新请求缓存"""
        self._request_cache[cache_key] = (time.time(), response)
        
        # 清理过期缓存
        current_time = time.time()
        expired_keys = [k for k, (timestamp, _) in self._request_cache.items() 
                       if current_time - timestamp > self._cache_ttl]
        for key in expired_keys:
            del self._request_cache[key]
    
    async def _request(self, method: str, endpoint: str, params: Dict[str, Any] = None, 
                      json_data: Dict[str, Any] = None, retry_count: int = 0) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: 请求方法（GET, POST等）
            endpoint: API端点
            params: URL参数
            json_data: JSON请求体
            retry_count: 当前重试次数
            
        Returns:
            API响应的JSON数据
            
        Raises:
            HiFlyAPIError: API返回错误
        """
        # 确保客户端存在
        self._ensure_client()
        
        # 修正URL构建逻辑
        if endpoint.startswith('/'):
            # 如果endpoint以/开头，使用urljoin
            url = urljoin(self.base_url, endpoint)
        else:
            # 否则，手动拼接路径
            url = f"{self.base_url}/{endpoint}"
        
        # 生成请求ID
        request_id = str(uuid.uuid4())[:8]
        
        # 检查缓存（仅对GET请求启用缓存）
        cache_key = None
        if method == "GET":
            cache_key = self._get_cache_key(method, url, params, json_data)
            cached_response = self._check_cache(cache_key)
            if cached_response:
                return cached_response
        
        try:
            # 添加更详细的日志记录
            logger.info(f"[{request_id}] 发送请求: {method} {url}")
            logger.info(f"[{request_id}] 请求头: {self.client.headers}")
            logger.info(f"[{request_id}] 请求参数: {params}")
            if json_data:
                logger.info(f"[{request_id}] 请求数据: {json.dumps(json_data)}")
            
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data
            )
            
            # 添加响应日志
            logger.info(f"[{request_id}] 响应状态码: {response.status_code}")
            logger.info(f"[{request_id}] 响应内容: {response.text}")
            
            # 处理非200响应
            if response.status_code != 200:
                error_msg = f"HTTP Error {response.status_code}: {response.text}"
                logger.error(f"[{request_id}] {error_msg}")
                
                # 处理认证错误
                if response.status_code == 401:
                    raise HiFlyAPIError(2003, "无效Token", None)
                
                # 如果可以重试，则重试
                if retry_count < self.max_retries:
                    logger.info(f"[{request_id}] Retrying request ({retry_count + 1}/{self.max_retries})...")
                    await asyncio.sleep(self.retry_delay)
                    return await self._request(method, endpoint, params, json_data, retry_count + 1)
                
                raise HiFlyAPIError(response.status_code, error_msg, None)
            
            # 解析响应
            response_data = response.json()
            
            # 检查API错误
            if response_data.get("code", 0) != 0:
                code = response_data.get("code")
                message = response_data.get("message") or self.ERROR_CODES.get(code, "未知错误")
                api_request_id = response_data.get("request_id")
                
                error_msg = f"API Error {code}: {message} (Request ID: {api_request_id})"
                logger.error(f"[{request_id}] {error_msg}")
                
                # 如果可以重试，则重试（某些错误码不应该重试）
                non_retryable_codes = [1002, 1005, 1006, 1009, 1011, 1013, 1015, 2003, 2011, 2012]
                if code not in non_retryable_codes and retry_count < self.max_retries:
                    logger.info(f"[{request_id}] Retrying request ({retry_count + 1}/{self.max_retries})...")
                    await asyncio.sleep(self.retry_delay)
                    return await self._request(method, endpoint, params, json_data, retry_count + 1)
                
                raise HiFlyAPIError(code, message, api_request_id)
            
            # 更新缓存（仅对GET请求）
            if method == "GET" and cache_key:
                self._update_cache(cache_key, response_data)
            
            return response_data
            
        except httpx.RequestError as e:
            error_msg = f"Request Error: {str(e)}"
            logger.error(f"[{request_id}] {error_msg}")
            
            # 检查是否是客户端关闭错误
            if "client has been closed" in str(e) and retry_count < self.max_retries:
                logger.info(f"[{request_id}] Client was closed, recreating and retrying...")
                self._create_client()
                return await self._request(method, endpoint, params, json_data, retry_count + 1)
            
            # 如果可以重试，则重试
            if retry_count < self.max_retries:
                logger.info(f"[{request_id}] Retrying request ({retry_count + 1}/{self.max_retries})...")
                await asyncio.sleep(self.retry_delay)
                return await self._request(method, endpoint, params, json_data, retry_count + 1)
            
            raise HiFlyAPIError(-1, f"请求错误: {str(e)}", None)
    
    async def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送GET请求"""
        return await self._request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送POST请求"""
        return await self._request("POST", endpoint, json_data=json_data)

    # ===== 数字人克隆 API =====
    
    async def create_avatar_by_video(self, title: str, video_url: str = None, file_id: str = None) -> Dict[str, Any]:
        """
        创建视频数字人
        
        Args:
            title: 数字人名称
            video_url: 视频URL，与file_id二选一必填
            file_id: 文件ID，与video_url二选一必填
            
        Returns:
            包含task_id的响应
        """
        if not video_url and not file_id:
            raise ValueError("video_url和file_id必须提供一个")
            
        data = {"title": title}
        if video_url:
            data["video_url"] = video_url
        if file_id:
            data["file_id"] = file_id
            
        #  
        return await self.post("avatar/create_by_video", json_data=data)
    
    async def create_avatar_by_image(self, title: str, image_url: str = None, 
                                   file_id: str = None, model: int = 2) -> Dict[str, Any]:
        """
        创建图片数字人
        
        Args:
            title: 数字人名称
            image_url: 图片URL，与file_id二选一必填
            file_id: 文件ID，与image_url二选一必填
            model: 模型类型，1:视频2.0，2:视频2.1，默认2
            
        Returns:
            包含task_id的响应
        """
        if not image_url and not file_id:
            raise ValueError("image_url和file_id必须提供一个")
            
        data = {"title": title, "model": model}
        if image_url:
            data["image_url"] = image_url
        if file_id:
            data["file_id"] = file_id
            
        return await self.post("avatar/create_by_image", json_data=data)
    
    async def get_avatar_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询数字人克隆任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            包含任务状态的响应
        """
        return await self.get("avatar/task", params={"task_id": task_id})
    
    async def get_avatar_list(self, page: int = 1, size: int = 20, kind: int = 2) -> Dict[str, Any]:
        """
        查询公共数字人列表
        
        Args:
            page: 页码，默认1
            size: 每页数量，默认20
            kind: 数字人分类，2:公共数字人，默认2
            
        Returns:
            包含数字人列表的响应
        """
        logger.info(f"调用API查询公共数字人列表: page={page}, size={size}, kind={kind}")
        try:
            # 修正：使用完整的API路径，不要依赖urljoin的行为
            # 因为base_url已经包含了/api/v2/hifly，所以endpoint不应该以/开头
            result = await self.get("avatar/list", params={"page": page, "size": size, "kind": kind})
            logger.info(f"API返回结果: {result}")
            return result
        except Exception as e:
            logger.error(f"查询公共数字人列表失败: {str(e)}")
            raise
    
    # ===== 声音克隆 API =====
    
    async def create_voice(self, title: str, voice_type: int = 8, 
                         audio_url: str = None, file_id: str = None) -> Dict[str, Any]:
        """
        创建声音
        
        Args:
            title: 声音名称
            voice_type: 声音类型，8:声音克隆基础版v2，默认8
            audio_url: 音频URL，与file_id二选一必填
            file_id: 文件ID，与audio_url二选一必填
            
        Returns:
            包含task_id的响应
        """
        if not audio_url and not file_id:
            raise ValueError("audio_url和file_id必须提供一个")
            
        data = {"title": title, "voice_type": voice_type}
        if audio_url:
            data["audio_url"] = audio_url
        if file_id:
            data["file_id"] = file_id
            
        return await self.post("voice/create", json_data=data)
    
    async def edit_voice(self, voice: str, rate: str = "1.0", 
                       volume: str = "1.0", pitch: str = "1.0") -> Dict[str, Any]:
        """
        修改声音参数
        
        Args:
            voice: 声音标识
            rate: 语速，值为0.5和2.0之间，默认1.0
            volume: 音量，值为0.1和2.0之间，默认1.0
            pitch: 语调，值为0.1和2.0之间，默认1.0
            
        Returns:
            API响应
        """
        data = {
            "voice": voice,
            "rate": rate,
            "volume": volume,
            "pitch": pitch
        }
        return await self.post("voice/edit", json_data=data)
    
    async def get_voice_list(self, page: int = 1, size: int = 20, kind: int = 1) -> Dict[str, Any]:
        """
        查询声音列表
        
        Args:
            page: 页码，默认1
            size: 每页数量，默认20
            kind: 声音分类，1:自己克隆的，2:公共声音，默认1
            
        Returns:
            包含声音列表的响应
        """
        return await self.get("voice/list", params={"page": page, "size": size, "kind": kind})
    
    async def get_voice_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询声音克隆任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            包含任务状态的响应
        """
        return await self.get("voice/task", params={"task_id": task_id})
    
    # ===== 视频创作 API =====
    
    async def create_video_by_audio(self, avatar: str, audio_url: str = None, 
                                  file_id: str = None, title: str = "未命名") -> Dict[str, Any]:
        """
        声音驱动视频创作
        
        Args:
            avatar: 数字人标识
            audio_url: 音频URL，与file_id二选一必填
            file_id: 文件ID，与audio_url二选一必填
            title: 作品名称，默认"未命名"
            
        Returns:
            包含task_id的响应
        """
        if not audio_url and not file_id:
            raise ValueError("audio_url和file_id必须提供一个")
            
        data = {"avatar": avatar, "title": title}
        if audio_url:
            data["audio_url"] = audio_url
        if file_id:
            data["file_id"] = file_id
            
        return await self.post("video/create_by_audio", json_data=data)
    
    async def create_video_by_tts(self, avatar: str, voice: str, text: str, 
                                title: str = "未命名", st_show: int = 0, **kwargs) -> Dict[str, Any]:
        """
        文本驱动视频创作
        
        Args:
            avatar: 数字人标识
            voice: 声音标识
            text: 文本内容
            title: 作品名称，默认"未命名"
            st_show: 是否显示字幕，1:显示，0:不显示，默认不显示
            **kwargs: 其他字幕相关参数
            
        Returns:
            包含task_id的响应
        """
        data = {
            "avatar": avatar,
            "voice": voice,
            "text": text,
            "title": title,
            "st_show": st_show
        }
        
        # 添加字幕相关参数
        subtitle_params = [
            "st_font_name", "st_font_size", "st_primary_color", 
            "st_outline_color", "st_width", "st_height", 
            "st_pos_x", "st_pos_y"
        ]
        
        for param in subtitle_params:
            if param in kwargs:
                data[param] = kwargs[param]
                
        return await self.post("video/create_by_tts", json_data=data)
    
    async def get_video_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询视频创作任务状态,包括视频和音频
        
        Args:
            task_id: 任务ID
            
        Returns:
            包含任务状态的响应
            示例：{
  "code": 0,
  "message": "",
  "status": 3,
  "video_Url": "https://example.com/videos/abc123.mp4?token=xyz789",
  "duration": 45,
  "request_id": "req123456789"
}
        """
        return await self.get("video/task", params={"task_id": task_id})
    
    # ===== 音频创作 API =====
    
    async def create_audio_by_tts(self, voice: str, text: str, title: str = "未命名") -> Dict[str, Any]:
        """
        文本转语音创建音频
        
        Args:
            voice: 声音标识
            text: 文本内容
            title: 作品名称，默认"未命名"
            
        Returns:
            包含task_id的响应
        """
        data = {
            "voice": voice,
            "text": text,
            "title": title
        }
        return await self.post("audio/create_by_tts", json_data=data)
    
    async def get_audio_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询视频创作任务状态,包括视频和音频,音频的返回结果与视频的返回结果相同，同一个接口请求
        
        Args:
            task_id: 任务ID
            
        Returns:
            包含任务状态的响应
            示例：{
  "code": 0,
  "message": "",
  "status": 3,
  "video_Url": "https://example.com/videos/abc123.mp4?token=xyz789",
  "duration": 45,
  "request_id": "req123456789"
}
        """
        return await self.get("video/task", params={"task_id": task_id})
    
    
    # ===== 账户 API =====
    
    async def get_account_credit(self) -> Dict[str, Any]:
        """
        查询账户积分
        
        Returns:
            包含积分信息的响应
        """
        return await self.get("account/credit")

# 确保在文件顶部导入asyncio 