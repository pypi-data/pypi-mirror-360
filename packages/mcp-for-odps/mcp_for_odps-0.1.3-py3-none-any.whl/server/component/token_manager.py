import asyncio
import httpx
import time
import logging
import os
from typing import Optional, Dict

# 设置日志
logger = logging.getLogger(__name__)

# 从环境变量读取OAuth配置
OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "")
OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "")
OAUTH_SCOPE = os.getenv("OAUTH_SCOPE", "odps.readonly")

class TokenManager:
    """OAuth Token管理器"""
    
    def __init__(self, 
                 client_id: Optional[str] = None,
                 client_secret: Optional[str] = None,
                 redirect_uri: Optional[str] = None,
                 scope: Optional[str] = None):
        """
        初始化TokenManager
        
        Args:
            client_id: OAuth客户端ID，如果为None则从环境变量读取
            client_secret: OAuth客户端密钥，如果为None则从环境变量读取
            redirect_uri: 重定向URI，如果为None则从环境变量读取
            scope: 授权范围，如果为None则从环境变量读取
        """
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.expires_at: Optional[float] = None
        self.refresh_task: Optional[asyncio.Task] = None
        
        # 从环境变量或参数获取OAuth配置
        self.client_id = client_id or OAUTH_CLIENT_ID
        self.client_secret = client_secret or OAUTH_CLIENT_SECRET
        self.redirect_uri = redirect_uri or OAUTH_REDIRECT_URI
        self.scope = scope or OAUTH_SCOPE
        
        self._lock = asyncio.Lock()
        
        # 验证必要的OAuth配置
        self._validate_oauth_config()
    
    def _validate_oauth_config(self):
        """验证OAuth配置"""
        missing_configs = []
        
        if not self.client_id:
            missing_configs.append("OAUTH_CLIENT_ID")
        if not self.client_secret:
            missing_configs.append("OAUTH_CLIENT_SECRET")
        if not self.redirect_uri:
            missing_configs.append("OAUTH_REDIRECT_URI")
            
        if missing_configs:
            logger.warning(f"缺少OAuth配置环境变量: {', '.join(missing_configs)}")
            logger.warning("如果需要OAuth认证，请设置相应的环境变量")
    
    def get_auth_url(self) -> str:
        """获取OAuth授权URL"""
        if not all([self.client_id, self.redirect_uri, self.scope]):
            raise ValueError("OAuth配置不完整，无法生成授权URL")
            
        auth_url = f"https://signin.aliyun.com/oauth2/v1/auth?client_id={self.client_id}&response_type=code&redirect_uri={self.redirect_uri}&scope={self.scope}"
        return auth_url
    
    async def initialize(self, client_id: Optional[str] = None, client_secret: Optional[str] = None, redirect_uri: Optional[str] = None, scope: Optional[str] = None):
        """初始化token管理器（可选，如果构造时未设置）"""
        if client_id:
            self.client_id = client_id
        if client_secret:
            self.client_secret = client_secret
        if redirect_uri:
            self.redirect_uri = redirect_uri
        if scope:
            self.scope = scope
            
        # 重新验证配置
        self._validate_oauth_config()
        
        # 获取授权URL
        try:
            auth_url = self.get_auth_url()
            logger.info(f"请访问以下URL进行授权: {auth_url}")
        except ValueError as e:
            logger.error(f"无法生成授权URL: {e}")
        
    async def get_initial_token(self, code: str, redirect_uri: Optional[str] = None):
        """使用授权码获取初始token"""
        # 如果没有提供redirect_uri，使用实例的配置
        redirect_uri = redirect_uri or self.redirect_uri
        if not redirect_uri:
            raise ValueError("redirect_uri未配置")
        async with self._lock:
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        "https://oauth.aliyun.com/v1/token",
                        json={
                            "grant_type": "authorization_code",
                            "code": code,
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                            "redirect_uri": redirect_uri
                        },
                        headers={
                            "Content-Type": "application/json"
                        }
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"获取access_token失败: {response.text}")
                    
                    token_data = response.json()
                    await self._update_tokens(token_data)
                    
                except Exception as e:
                    logger.error(f"获取初始token失败: {e}")
                    raise
    
    async def _update_tokens(self, token_data: Dict):
        """更新token信息并启动刷新任务"""
        self.access_token = token_data.get("access_token")
        self.refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)  # 默认1小时
        
        # 计算过期时间（提前10秒刷新）
        self.expires_at = time.time() + expires_in - 10
        
        logger.info(f"Token更新成功，将在{expires_in-10}秒后自动刷新")
        
        # 取消之前的刷新任务
        if self.refresh_task and not self.refresh_task.done():
            self.refresh_task.cancel()
        
        # 启动新的刷新任务
        self.refresh_task = asyncio.create_task(self._schedule_refresh())
    
    async def _schedule_refresh(self):
        """定时刷新token"""
        try:
            # 等待到刷新时间
            wait_time = self.expires_at - time.time()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            # 执行刷新
            await self._refresh_access_token()
            
        except asyncio.CancelledError:
            logger.info("Token刷新任务被取消")
        except Exception as e:
            logger.error(f"定时刷新token失败: {e}")
    
    async def _refresh_access_token(self):
        """刷新access token"""
        async with self._lock:
            if not self.refresh_token:
                raise Exception("没有refresh_token，无法刷新")
            
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(
                        "https://oauth.aliyun.com/v1/token",
                        json={
                            "grant_type": "refresh_token",
                            "refresh_token": self.refresh_token,
                            "client_id": self.client_id,
                            "client_secret": self.client_secret,
                        },
                        headers={
                            "Content-Type": "application/json"
                        }
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"刷新token失败: {response.text}")
                    
                    token_data = response.json()
                    await self._update_tokens(token_data)
                    logger.info("Token刷新成功")
                    
                except Exception as e:
                    logger.error(f"刷新token失败: {e}")
                    raise
    
    async def get_valid_token(self) -> str:
        """获取有效的access token"""
        async with self._lock:
            # 检查token是否即将过期
            if self.expires_at and time.time() >= self.expires_at - 30:
                logger.info("Token即将过期，立即刷新")
                await self._refresh_access_token()
            
            if not self.access_token:
                raise Exception("没有有效的access_token")
            
            return self.access_token
    
    def cleanup(self):
        """清理资源"""
        if self.refresh_task and not self.refresh_task.done():
            self.refresh_task.cancel()

# 全局TokenManager实例
_global_token_manager: Optional[TokenManager] = None

def get_global_token_manager() -> TokenManager:
    """获取全局TokenManager实例"""
    global _global_token_manager
    if _global_token_manager is None:
        _global_token_manager = TokenManager()
    return _global_token_manager

def create_token_manager(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    scope: Optional[str] = None
) -> TokenManager:
    """创建TokenManager实例的工厂函数"""
    return TokenManager(client_id, client_secret, redirect_uri, scope)

# 便捷函数（保持向后兼容）
async def setup_oauth(
    token_manager: TokenManager, 
    client_id: Optional[str] = None, 
    client_secret: Optional[str] = None, 
    redirect_uri: Optional[str] = None, 
    scope: Optional[str] = None
):
    """设置OAuth认证"""
    await token_manager.initialize(client_id, client_secret, redirect_uri, scope)

async def complete_oauth_with_code(token_manager: TokenManager, code: str, redirect_uri: Optional[str] = None):
    """使用授权码完成OAuth流程"""
    await token_manager.get_initial_token(code, redirect_uri) 