# MCP ODPS 测试客户端

这是一个专门为ODPS MCP服务器设计的集成测试客户端，支持通过stdio协议连接并测试所有MCP工具功能。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装MCP Python库
pip install mcp

# 或者如果有requirements.txt
pip install -r ../requirements.txt
```

### 2. 运行测试

```bash
# 进入客户端目录
cd client

# 运行所有测试
python run_test.py

# 查看帮助信息
python run_test.py --help
```

### 3. 直接运行测试客户端

```bash
# 直接运行测试客户端（需要手动设置环境变量）
python mcp_client.py
```

## 📁 文件结构

```
client/
├── mcp_client.py       # 主测试客户端
├── run_test.py         # 测试运行脚本
├── config.json         # Mock数据和测试配置
├── test_config.env     # 测试环境变量
├── test_report.json    # 测试报告（运行后生成）
└── README.md          # 本文档
```

## 🧪 测试内容

### 功能测试
- ✅ **get_table_info** - 测试获取表信息功能
- ✅ **execute_sql** - 测试SQL执行功能
- ✅ **OAuth环境变量** - 测试OAuth配置

### 连接测试
- ✅ **stdio连接** - 测试MCP服务器stdio协议连接
- ✅ **工具发现** - 测试可用工具列表获取
- ✅ **工具调用** - 测试各种参数的工具调用

### 数据验证
- ✅ **响应结构** - 验证返回数据结构正确性
- ✅ **字段完整性** - 检查必需字段是否存在
- ✅ **错误处理** - 测试异常情况处理

## 🔧 配置说明

### 环境变量 (`test_config.env`)

```bash
# MaxCompute 基础配置
MAXCOMPUTE_PROJECT_NAME=test_project
MAXCOMPUTE_SCHEMA_NAME=default
MAXCOMPUTE_BASE_URL=https://maxcompute.cn-hangzhou.aliyuncs.com

# OAuth 认证配置（测试用）
OAUTH_CLIENT_ID=test_client_id
OAUTH_CLIENT_SECRET=test_client_secret
OAUTH_REDIRECT_URI=http://localhost:8080/callback
OAUTH_SCOPE=odps.readonly

# 测试配置
TEST_MODE=true
MOCK_DATA=true
```

### Mock数据配置 (`config.json`)

Mock数据包含预定义的表结构，用于测试而不需要真实的MaxCompute连接：

```json
{
  "mock_data": {
    "tables": [
      {
        "tableName": "user_info",
        "columns": [...],
        "partitions": [...],
        "ddl": "CREATE TABLE ..."
      }
    ]
  }
}
```

## 📊 测试报告

运行测试后会生成 `test_report.json` 文件，包含详细的测试结果：

```json
[
  {
    "tool_name": "get_table_info",
    "total_tests": 3,
    "passed": 3,
    "failed": 0,
    "details": [...]
  }
]
```

## 🛠️ 自定义测试

### 添加新的测试用例

在 `mcp_client.py` 中的测试方法中添加新的测试用例：

```python
async def test_get_table_info(self):
    test_cases = [
        {
            "name": "你的测试名称",
            "args": {"tableNameList": ["your_table"]},
            "expected_fields": ["tableName", "columns"]
        }
    ]
```

### 添加新的Mock数据

在 `config.json` 的 `mock_data.tables` 数组中添加新表：

```json
{
  "tableName": "new_table",
  "columns": [...],
  "partitions": [...],
  "ddl": "CREATE TABLE ..."
}
```

## 🐛 故障排除

### 常见问题

1. **连接失败**
   ```
   ❌ 连接MCP服务器失败
   ```
   - 检查 `application.py` 路径是否正确
   - 确保在项目根目录运行
   - 检查Python环境和依赖

2. **导入错误**
   ```
   ❌ 导入测试模块失败: No module named 'mcp'
   ```
   - 安装MCP库: `pip install mcp`

3. **工具未找到**
   ```
   ⚠️  get_table_info 工具未找到
   ```
   - 检查服务器是否正常启动
   - 验证工具注册是否正确

### 调试模式

设置日志级别来获取更多调试信息：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 最佳实践

1. **定期运行测试** - 在每次修改后运行测试确保功能正常
2. **更新Mock数据** - 保持Mock数据与真实API结构一致
3. **检查测试报告** - 分析失败原因并及时修复
4. **环境隔离** - 使用专门的测试环境变量配置

## 📝 开发说明

这个测试客户端使用：
- **mcp库** - 用于MCP协议通信
- **asyncio** - 异步操作支持
- **httpx** - HTTP客户端（如果需要）
- **pathlib** - 路径处理

测试客户端设计为：
- 🔄 **自包含** - 不依赖外部服务
- 🧪 **Mock友好** - 支持Mock数据测试
- 📈 **可扩展** - 易于添加新测试
- 📊 **详细报告** - 提供完整测试结果 