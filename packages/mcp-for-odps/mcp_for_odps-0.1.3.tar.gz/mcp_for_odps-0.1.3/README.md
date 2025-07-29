# MCP for ODPS

MaxCompute (ODPS) API工具，用于获取表的详细信息，包括表名、字段信息、分区信息和DDL。

## 环境变量配置

在使用本工具之前，请配置以下环境变量：

### 必需的环境变量

- `MAXCOMPUTE_PROJECT_NAME`: MaxCompute项目名称

### 可选的环境变量

- `MAXCOMPUTE_SCHEMA_NAME`: Schema名称（默认值：`default`）
- `MAXCOMPUTE_BASE_URL`: MaxCompute API基础URL（默认值：`https://maxcompute.cn-hangzhou.aliyuncs.com`）

### OAuth认证环境变量（如果需要OAuth认证）

- `OAUTH_CLIENT_ID`: OAuth客户端ID
- `OAUTH_CLIENT_SECRET`: OAuth客户端密钥
- `OAUTH_REDIRECT_URI`: OAuth重定向URI
- `OAUTH_SCOPE`: OAuth授权范围（默认值：`odps.readonly`）

### 配置示例

```bash
# 在 .env 文件中配置
MAXCOMPUTE_PROJECT_NAME=your_project_name
MAXCOMPUTE_SCHEMA_NAME=default
MAXCOMPUTE_BASE_URL=https://maxcompute.cn-hangzhou.aliyuncs.com

# OAuth认证配置（可选）
OAUTH_CLIENT_ID=your_oauth_client_id
OAUTH_CLIENT_SECRET=your_oauth_client_secret
OAUTH_REDIRECT_URI=your_redirect_uri
OAUTH_SCOPE=odps.readonly
```

或者在命令行中设置：

```bash
export MAXCOMPUTE_PROJECT_NAME=your_project_name
export MAXCOMPUTE_SCHEMA_NAME=default
export MAXCOMPUTE_BASE_URL=https://maxcompute.cn-hangzhou.aliyuncs.com

# OAuth认证配置（可选）
export OAUTH_CLIENT_ID=your_oauth_client_id
export OAUTH_CLIENT_SECRET=your_oauth_client_secret
export OAUTH_REDIRECT_URI=your_redirect_uri
export OAUTH_SCOPE=odps.readonly
```

## 使用方法

### 获取表信息

```python
# 使用全局配置获取表信息
result = await get_table_info(['table1', 'table2'])
```

### API功能

- **并发请求**: 支持同时获取多个表的信息，提高查询效率
- **完整信息**: 返回表的完整信息，包括字段、分区、DDL等
- **错误处理**: 详细的错误信息和日志记录
- **JSON格式**: 返回结构化的JSON数据

### 返回数据格式

```json
{
  "success": [
    {
      "tableName": "表名",
      "projectName": "项目名",
      "schema": "schema名",
      "owner": "所有者",
      "type": "表类型",
      "creationTime": "创建时间",
      "lastModifiedTime": "最后修改时间",
      "lifecycle": "生命周期",
      "comment": "表注释",
      "createTableDDL": "建表DDL",
      "columns": [
        {
          "name": "字段名",
          "type": "字段类型",
          "comment": "字段注释",
          "isNullable": true
        }
      ],
      "partitionColumns": [
        {
          "name": "分区字段名",
          "type": "分区字段类型",
          "comment": "分区字段注释",
          "isNullable": false
        }
      ]
    }
  ],
  "failed": [
    {
      "tableName": "失败的表名",
      "error": "错误信息"
    }
  ]
}
```

## 🧪 测试

项目包含完整的集成测试客户端，用于验证所有功能：

### 运行测试

```bash
# 进入测试客户端目录
cd client

# 运行所有测试
python run_test.py
```

### 测试内容
- ✅ **get_table_info** 工具功能测试
- ✅ **execute_sql** 工具功能测试（开发中）
- ✅ **OAuth环境变量** 配置测试
- ✅ **MCP连接** 和通信测试

测试客户端使用Mock数据，无需真实的MaxCompute环境即可完成功能验证。详细说明请参考 [`client/README.md`](client/README.md)。

## 开发

### 项目结构

```
mcp_for_odps/
├── application.py          # MCP工具主文件
├── component/
│   ├── __init__.py        # 组件导出
│   ├── token_manager.py   # OAuth认证管理
│   └── get_table_info.py  # 表信息获取API
├── client/                 # 测试客户端
│   ├── mcp_client.py      # 主测试客户端
│   ├── run_test.py        # 测试运行脚本
│   ├── config.json        # Mock数据配置
│   ├── test_config.env    # 测试环境变量
│   └── README.md          # 测试说明文档
├── main.py
├── pyproject.toml
└── README.md
```

### 依赖

- `httpx`: HTTP客户端
- `mcp[cli]`: MCP框架
- `openai`: OpenAI客户端

## 注意事项

1. 确保设置了正确的环境变量
2. MaxCompute项目需要有相应的访问权限
3. 网络环境需要能够访问MaxCompute API
4. 建议在生产环境中使用适当的日志级别
