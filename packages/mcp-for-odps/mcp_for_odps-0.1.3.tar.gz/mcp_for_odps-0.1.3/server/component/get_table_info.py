import asyncio
import httpx
import json
import logging
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from .token_manager import create_token_manager

# 设置日志
logger = logging.getLogger(__name__)

# 从环境变量读取全局配置
MAXCOMPUTE_PROJECT_NAME = os.getenv("MAXCOMPUTE_PROJECT_NAME", "")
MAXCOMPUTE_SCHEMA_NAME = os.getenv("MAXCOMPUTE_SCHEMA_NAME", "default")
MAXCOMPUTE_BASE_URL = os.getenv("MAXCOMPUTE_BASE_URL", "https://maxcompute.cn-hangzhou.aliyuncs.com")

# 测试模式配置
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
MOCK_DATA = os.getenv("MOCK_DATA", "false").lower() == "true"

@dataclass
class ColumnInfo:
    """列信息数据类"""
    name: str
    type: str
    comment: str
    isNullable: bool = True

@dataclass
class TableInfo:
    """表信息数据类"""
    tableName: str
    comment: str = ""
    createTableDDL: str = ""
    columns: List[ColumnInfo] = None
    partitionColumns: List[ColumnInfo] = None

    def __post_init__(self):
        """初始化默认值"""
        if self.columns is None:
            self.columns = []
        if self.partitionColumns is None:
            self.partitionColumns = []

class MaxComputeAPI:
    """MaxCompute API封装类"""
    
    def __init__(self, 
                 base_url: Optional[str] = None, 
                 project_name: Optional[str] = None, 
                 schema_name: Optional[str] = None):
        """
        初始化MaxComputeAPI
        
        Args:
            base_url: API基础URL，如果为None则从环境变量读取
            project_name: 项目名，如果为None则从环境变量读取
            schema_name: Schema名，如果为None则从环境变量读取
        """
        self.base_url = base_url or MAXCOMPUTE_BASE_URL
        self.project_name = project_name or MAXCOMPUTE_PROJECT_NAME
        self.schema_name = schema_name or MAXCOMPUTE_SCHEMA_NAME
        
        # 验证必要参数（在非测试模式下）
        if not TEST_MODE and not self.project_name:
            raise ValueError("MAXCOMPUTE_PROJECT_NAME environment variable must be set or project_name must be provided")
        
        # 在非测试模式下才创建token管理器
        self.token_manager = None if TEST_MODE else create_token_manager()
        
        # 加载Mock数据
        self.mock_data = self._load_mock_data() if MOCK_DATA else {}
    
    def _load_mock_data(self) -> Dict[str, Any]:
        """加载Mock数据"""
        try:
            # 尝试从client目录加载config.json
            config_paths = [
                Path(__file__).parent.parent / "client" / "config.json",
                Path(__file__).parent / "config.json",
                Path("client/config.json"),
                Path("config.json")
            ]
            
            for config_path in config_paths:
                if config_path.exists():
                    logger.info(f"加载Mock数据从: {config_path}")
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        return config.get("mock_data", {})
            
            logger.warning("未找到Mock数据配置文件，使用默认数据")
            return self._get_default_mock_data()
            
        except Exception as e:
            logger.error(f"加载Mock数据失败: {e}")
            return self._get_default_mock_data()
    
    def _get_default_mock_data(self) -> Dict[str, Any]:
        """获取默认Mock数据"""
        return {
            "tables": [
                {
                    "tableName": "user_info",
                    "columns": [
                        {"name": "user_id", "type": "bigint", "comment": "用户ID"},
                        {"name": "username", "type": "string", "comment": "用户名"},
                        {"name": "email", "type": "string", "comment": "邮箱"}
                    ],
                    "partitions": [
                        {"name": "ds", "type": "string", "comment": "分区日期"}
                    ],
                    "ddl": "CREATE TABLE user_info (...)"
                }
            ]
        }
    
    def _get_mock_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """获取Mock表信息"""
        tables = self.mock_data.get("tables", [])
        for table in tables:
            if table.get("tableName") == table_name:
                return {
                    "tableName": table_name,
                    "comment": table.get("comment", ""),
                    "createTableDDL": table.get("ddl", ""),
                    "columns": table.get("columns", []),
                    "partitions": table.get("partitions", [])
                }
        return None
    
    async def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        access_token = await self.token_manager.get_valid_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    
    def _parse_column_info(self, col_data: Dict[str, Any]) -> ColumnInfo:
        """解析列信息"""
        return ColumnInfo(
            name=col_data.get("name", ""),
            type=col_data.get("type", ""),
            comment=col_data.get("comment", ""),
            isNullable=col_data.get("isNullable", True)
        )
    
    def _parse_table_info(self, table_name: str, table_data: Dict[str, Any]) -> TableInfo:
        """解析表信息"""
        # 创建基本表信息
        table_info = TableInfo(
            tableName=table_name,
            comment=table_data.get("comment", ""),
            createTableDDL=table_data.get("createTableDDL", "")
        )
        
        # 解析普通列信息
        for col in table_data.get("nativeColumns", []):
            table_info.columns.append(self._parse_column_info(col))
        
        # 解析分区列信息
        for col in table_data.get("partitionColumns", []):
            table_info.partitionColumns.append(self._parse_column_info(col))
        
        return table_info
    
    async def fetch_table_info(self, client: httpx.AsyncClient, table_name: str) -> Dict[str, Any]:
        """异步获取单个表的详细信息"""
        try:
            # 如果启用Mock数据，直接返回Mock结果
            if MOCK_DATA:
                mock_info = self._get_mock_table_info(table_name)
                if mock_info:
                    logger.info(f"返回Mock数据 for table: {table_name}")
                    return {
                        "status": "success",
                        "data": mock_info
                    }
                else:
                    return {
                        "status": "error",
                        "tableName": table_name,
                        "error": f"Mock数据中未找到表: {table_name}"
                    }
            
            # 真实API调用逻辑
            # 构建API请求URL和参数
            url = f"{self.base_url}/api/v1/projects/{self.project_name}/tables/{table_name}"
            params = {"schemaName": self.schema_name}
            headers = await self._get_headers()
            
            # 发送GET请求
            response = await client.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                # 解析响应数据
                data = response.json()
                table_data = data.get("data", {})
                table_info = self._parse_table_info(table_name, table_data)
                
                return {
                    "status": "success",
                    "data": asdict(table_info)
                }
            else:
                # 处理错误响应
                error_msg = f"获取表 {table_name} 信息失败: HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f", 错误信息: {error_data}"
                except:
                    error_msg += f", 响应内容: {response.text}"
                logger.error(error_msg)
                return {
                    "status": "error",
                    "tableName": table_name,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = f"处理表 {table_name} 时发生异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "tableName": table_name,
                "error": error_msg
            }
    
    async def fetch_tables_info(self, table_names: List[str]) -> str:
        """批量获取表信息"""
        try:
            async with httpx.AsyncClient() as client:
                # 创建并发任务
                tasks = [self.fetch_table_info(client, name) for name in table_names]
                results = await asyncio.gather(*tasks)
            
            # 处理结果
            response = {"success": [], "failed": []}
            for result in results:
                if result["status"] == "success":
                    response["success"].append(result["data"])
                else:
                    response["failed"].append({
                        "tableName": result["tableName"],
                        "error": result["error"]
                    })
            
            return json.dumps(response, ensure_ascii=False, indent=2)
            
        except Exception as e:
            error_msg = f"批量获取表信息失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({
                "success": [],
                "failed": [{"error": error_msg}]
            }, ensure_ascii=False, indent=2)
        finally:
            if self.token_manager:
                self.token_manager.cleanup()

# 全局API实例
_global_api: Optional[MaxComputeAPI] = None

def get_global_api() -> MaxComputeAPI:
    """获取全局API实例"""
    global _global_api
    if _global_api is None:
        _global_api = MaxComputeAPI()
    return _global_api

def create_maxcompute_api(
    base_url: Optional[str] = None, 
    project_name: Optional[str] = None, 
    schema_name: Optional[str] = None
) -> MaxComputeAPI:
    """创建MaxComputeAPI实例的工厂函数"""
    return MaxComputeAPI(base_url, project_name, schema_name)

async def fetch_tables_info(table_names: List[str]) -> str:
    """使用全局配置批量获取表信息的便捷函数"""
    api = get_global_api()
    return await api.fetch_tables_info(table_names) 