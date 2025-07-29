from .component import fetch_tables_info
from mcp.server import FastMCP
import sys

app = FastMCP('odps_api_tool')

##通过tableNameList获取表的详细信息
@app.tool()
async def get_table_info(tableNameList: list) -> str:
    '''
    通过tableNameList获取表的详细信息，包括表名、字段信息、分区信息和DDL
    使用环境变量配置的全局项目设置
    
    环境变量:
        MAXCOMPUTE_PROJECT_NAME: 项目名（必需）
        MAXCOMPUTE_SCHEMA_NAME: Schema名称（默认：default）
        MAXCOMPUTE_BASE_URL: API基础URL（默认：https://maxcompute.cn-hangzhou.aliyuncs.com）
    
    Args:
        tableNameList: 表名列表
    Returns:
        str: JSON格式的表详细信息
    '''
    return await fetch_tables_info(tableNameList) 


## 通过api的方式提交执行查询sql
@app.tool()
async def execute_sql(sql: str, projectName: str):
    pass


def main():
    """主函数，用于uvx运行"""
    show_startup_info()
    app.run(transport="stdio")

def show_startup_info():
    """显示启动信息"""
    print("🚀 MCP for ODPS 服务启动中...")
    print("=" * 50)
    
    # 检查环境变量
    import os
    project_name = os.getenv("MAXCOMPUTE_PROJECT_NAME", "")
    schema_name = os.getenv("MAXCOMPUTE_SCHEMA_NAME", "default")
    base_url = os.getenv("MAXCOMPUTE_BASE_URL", "https://maxcompute.cn-hangzhou.aliyuncs.com")
    
    print("🔧 环境配置检查：")
    config_ok = True
    
    # MaxCompute配置检查
    if project_name:
        print(f"   ✅ MAXCOMPUTE_PROJECT_NAME: {project_name}")
    else:
        print("   ❌ MAXCOMPUTE_PROJECT_NAME: 未设置")
        config_ok = False
    
    print(f"   📁 MAXCOMPUTE_SCHEMA_NAME: {schema_name}")
    print(f"   🌐 MAXCOMPUTE_BASE_URL: {base_url}")
    
    # OAuth配置检查
    oauth_client_id = os.getenv("OAUTH_CLIENT_ID", "")
    oauth_client_secret = os.getenv("OAUTH_CLIENT_SECRET", "")
    oauth_redirect_uri = os.getenv("OAUTH_REDIRECT_URI", "")
    oauth_scope = os.getenv("OAUTH_SCOPE", "odps.readonly")
    
    print("\n🔐 OAuth配置检查：")
    oauth_configured = True
    
    if oauth_client_id:
        print(f"   ✅ OAUTH_CLIENT_ID: {oauth_client_id}")
    else:
        print("   ⚠️  OAUTH_CLIENT_ID: 未设置")
        oauth_configured = False
        
    if oauth_client_secret:
        print(f"   ✅ OAUTH_CLIENT_SECRET: {'*' * len(oauth_client_secret)}")
    else:
        print("   ⚠️  OAUTH_CLIENT_SECRET: 未设置")
        oauth_configured = False
        
    if oauth_redirect_uri:
        print(f"   ✅ OAUTH_REDIRECT_URI: {oauth_redirect_uri}")
    else:
        print("   ⚠️  OAUTH_REDIRECT_URI: 未设置")
        oauth_configured = False
    
    print(f"   📋 OAUTH_SCOPE: {oauth_scope}")
    
    if not oauth_configured:
        print("   💡 OAuth认证为可选功能，如需使用请配置相应环境变量")
    
    print("\n📋 可用工具：")
    print("   🔍 get_table_info - 获取表详细信息")
    print("   💻 execute_sql - 执行SQL查询（开发中）")
    
    if config_ok:
        print("\n✅ 配置正常，MCP服务就绪")
        print("📡 等待客户端连接...")
    else:
        print("\n⚠️  配置不完整，请设置环境变量")
        print("   export MAXCOMPUTE_PROJECT_NAME=your_project_name")
    
    print("=" * 50)
    print("💡 提示：使用 --test 参数可以查看详细配置信息")
    print("=" * 50)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # 测试模式：显示详细配置信息
        main()
    elif len(sys.argv) > 1 and sys.argv[1] == "--help":
        # 帮助信息
        print("🚀 MCP for ODPS - MaxCompute API 工具")
        print("\n使用方法:")
        print("  python application.py          # 启动MCP服务")
        print("  python application.py --test   # 查看配置信息")
        print("  python application.py --help   # 显示帮助")
        print("\n环境变量:")
        print("  MAXCOMPUTE_PROJECT_NAME  # 项目名称（必需）")
        print("  MAXCOMPUTE_SCHEMA_NAME   # Schema名称（可选，默认：default）")
        print("  MAXCOMPUTE_BASE_URL      # API地址（可选）")
        print("\nOAuth认证环境变量（可选）:")
        print("  OAUTH_CLIENT_ID          # OAuth客户端ID")
        print("  OAUTH_CLIENT_SECRET      # OAuth客户端密钥")
        print("  OAUTH_REDIRECT_URI       # OAuth重定向URI")
        print("  OAUTH_SCOPE              # OAuth授权范围（默认：odps.readonly）")
    else:
        # 正常模式：启动MCP服务
        show_startup_info()
        app.run(transport="stdio")


