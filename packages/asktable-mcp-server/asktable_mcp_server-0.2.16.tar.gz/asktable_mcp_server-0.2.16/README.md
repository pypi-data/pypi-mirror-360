# Asktable-MCP-Server
![Case](https://s3.bmp.ovh/imgs/2025/07/02/a16c161e3570120b.png )

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/asktable-mcp-server.svg)](https://pypi.org/project/asktable-mcp-server/)

`asktable-mcp-server` 是为 [AskTable](https://www.asktable.com/) 提供的 MCP 服务，支持通过 Stdio 或 SSE 协议与 AskTable SaaS 或本地部署服务交互。

![Case](https://s3.bmp.ovh/imgs/2025/07/02/7de2a851031f6913.png)


---

## 工具介绍

### 可用工具

1. **list_data** - 获取当前APIKEY下的所有可用数据库（数据源）信息
   - **输入示例**：我数据库中有哪些数据源？
   - **输出**：数据源信息列表，包含数据源ID、数据库引擎、数据库描述
   - **使用场景**：查看用户权限下的所有数据源，获取数据源ID用于后续查询

2. **query** - 根据用户的问题，直接返回数据结果
   - **输入示例**：
     - "请给我出销售额前10的产品"
     - "昨天的订单总金额是多少"
     - "每个部门有多少员工"
   - **输出**：查询的实际数据结果
   - **使用场景**：需要直接获取查询答案，不关心SQL细节

3. **gen_sql** - 根据用户查询生成对应的SQL语句
   - **输入示例**：
     - "生成可以找出销售额前10的产品的sql"
     - "我需要查询昨天的订单总金额的sql"
     - "统计每个部门的员工数量的sql"
   - **输出**：生成的SQL语句
   - **使用场景**：需要查看生成的SQL语句，进行SQL审查或调试

---

## 用户配置指南

### 方式一：SaaS SSE 模式（推荐新用户）

如果您使用的是 AskTable SaaS 服务，推荐使用 SSE 方式，无需安装任何软件。


1. **获取 API 密钥和数据源 ID**
   - 登录 [AskTable](https://www.asktable.com/)
   - 在设置中获取您的 API 密钥(apikey)
   - 选择要连接的数据源，获取数据源 ID(datasource_id)

2. **配置 MCP 客户端（推荐 SSE 方式）**
   ```json
   {
     "mcpServers": {
       "asktable": {
         "type": "sse",
         "url": "https://mcp.asktable.com/sse/?apikey=ASKER_8H8DRJCH6LT8HCJPXOH4&datasource_id=ds_6iewvP4cpSyhO76P2Tv8MW",
         "headers": {},
         "timeout": 300,
         "sse_read_timeout": 300
       }
     }
   }
   ```
   > 注意: 上述 URL 中的 apikey 和 datasoruce_id 是在 AskTable.com 官网的演示项目和数据，可以直接拿来测试。比如问，总共多少学生？

3. **开始使用**
   - 重启您的 MCP 客户端
   - 现在可以使用 AskTable 的所有功能了！

### 方式二：SaaS Stdio 模式（需要安装包）

如果您使用 SaaS 服务但希望使用 Stdio 模式，需要本地安装包。

#### 1. 安装包
```bash
# 使用 uv 安装
uvx asktable-mcp-server@latest
```

#### 2. 配置 MCP 客户端

```json
{
  "mcpServers": {
    "asktable": {
      "command": "uvx",
      "args": ["asktable-mcp-server@latest"],
      "env": {
        "API_KEY": "ASKER_8H8DRJCH6LT8HCJPXOH4",
        "DATASOURCE_ID": "ds_6iewvP4cpSyhO76P2Tv8MW"
      }
    }
  }
}
```

**环境变量说明**：
- `API_KEY`：AskTable API 密钥（必需）
- `DATASOURCE_ID`：数据源ID（必需）

### 方式三：本地部署 SSE 模式

如果您使用 AskTable 本地部署版本，推荐使用 SSE 方式，在 AskTable 的 All-in-One 镜像中已经包含了 MCP SSE Server，默认地址是`http://your_local_host:port/mcp/sse`。

#### 配置 MCP 客户端

```json
{
  "mcpServers": {
    "asktable": {
      "type": "sse",
      "url": "http://your_local_host:port/mcp/sse/?apikey=your_api_key&datasource_id=your_datasource_id",
      "headers": {},
      "timeout": 300,
      "sse_read_timeout": 300
    }
  }
}
```

**参数说明**：
- `apikey`：AskTable API 密钥（必需）
- `datasource_id`：数据源ID（必需）

### 方式四：本地部署 Stdio 模式（需要安装包）

如果您使用本地部署但希望使用 Stdio 模式，需要本地安装包并配置 base_url。

#### 1. 安装包
```bash
# 使用 uv 安装
uvx asktable-mcp-server@latest
```

#### 2. 配置 MCP 客户端

```json
{
  "mcpServers": {
    "asktable": {
      "command": "uvx",
      "args": ["asktable-mcp-server@latest"],
      "env": {
        "API_KEY": "your_api_key",
        "DATASOURCE_ID": "your_datasource_id",
        "BASE_URL": "http://your_local_host:port/api"
      }
    }
  }
}
```

**环境变量说明**：
- `API_KEY`：AskTable API 密钥（必需）
- `DATASOURCE_ID`：数据源ID（必需）
- `BASE_URL`：本地部署服务地址（必需）



---

## 自建 SSE 服务（高级用户）


### Docker 部署（推荐）

#### 使用官方镜像
```bash
# 拉取镜像
docker pull registry.cn-shanghai.aliyuncs.com/datamini/asktable-mcp-server:latest

# 运行容器
docker run -d \
  --name asktable-mcp-server \
  -p 8095:8095 \
  -e API_KEY=your_api_key \
  -e DATASOURCE_ID=your_datasource_id \
  -e BASE_URL=http://your_local_ip:port/api \
  registry.cn-shanghai.aliyuncs.com/datamini/asktable-mcp-server:latest
```

---

如需进一步帮助，请查阅官方文档或联系我们。
