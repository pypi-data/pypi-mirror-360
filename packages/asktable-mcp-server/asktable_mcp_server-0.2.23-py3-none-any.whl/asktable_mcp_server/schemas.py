from typing import Annotated, Dict, Any, Optional
from pydantic import Field

# 共享的参数类型定义
QuestionParamGenSQL = Annotated[str, Field(description="用户的自然语言查询描述。示例：生成查询昨天订单总金额的SQL、写一个SQL查询销售额前10的产品、帮我写一个统计各部门员工数量的SQL")]
QuestionParamQuery = Annotated[str, Field(description="用户的自然语言查询描述。示例：查询昨天订单总金额、查询销售额前10的产品、统计各部门员工数量")]

RoleIdParam = Annotated[Optional[str], Field(description="角色ID，精确控制用户对数据的访问权限，支持库/表/字段/行四级控制。示例：'role_123456'，可以为空（使用默认权限）。详见：https://docs.asktable.com/docs/role-and-permission-management/introduction")]

RoleVariablesParam = Annotated[Optional[Dict[str, Any]], Field(description="角色变量，用于角色访问控制时的变量传递。示例：{'employee_id': 2}（限定员工可见范围）或{'department_id': 'dept_001'}（限定部门可见范围），可以为空（不使用变量限制）")]

# 共享的工具描述
GEN_SQL_DESCRIPTION = """
将自然语言查询转换为标准SQL语句。
这是一个智能SQL生成工具，可以理解用户的自然语言描述，并生成相应的SQL查询语句。
该工具仅返回SQL文本，不会执行查询操作。

适用场景：
    - 需要将业务需求快速转换为SQL查询语句
    - 在执行查询前想要检查和验证SQL语句
    - 需要获取SQL语句用于其他系统或工具
    - 学习或理解如何编写特定查询的SQL语句
"""

QUERY_DESCRIPTION = """
将自然语言查询转换为实际数据结果。
这是一个智能数据查询工具，可以理解用户的自然语言描述，并返回相应的查询结果。

适用场景：
    - 需要快速获取业务数据的查询结果
    - 直接获取数据分析结果和洞察
    - 需要以自然语言方式查询数据库
    - 获取实时数据报表和统计信息
    - 通过角色访问控制实现数据安全访问
"""

# HTML 模板
def get_home_page_html(version: str, base_url: str, path_prefix: str) -> str:
    """生成首页 HTML 内容"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>AskTable MCP 服务（SSE）</title>
        <style>
            body {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                line-height: 1.6;
            }}
            pre {{
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                overflow-x: auto;
            }}
            code {{
                white-space: pre-wrap;
            }}
            h1, h2 {{
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
            }}
            ul {{
                padding-left: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>欢迎访问 AskTable MCP 服务（SSE）!</h1>
        <p>当前版本: v{version}</p>

        <h2>配置示例</h2>
        <p>在您的 Agent 配置文件中，添加以下配置:</p>
        <pre><code>{{
    "mcpServers": {{
        "asktable": {{
            "type": "sse",
            "url": "{base_url}{path_prefix}/sse/?api_key=YOUR_API_KEY&datasource_id=YOUR_DATASOURCE_ID",
            "headers": {{}},
            "timeout": 300,
            "sse_read_timeout": 300
        }}
    }}
}}</code></pre>

        <h2>工具</h2>
        <ul>
            <li>使用 AskTable 生成 SQL</li>
            <li>使用 AskTable 查询数据</li>
            <li>列出 AskTable 中的所有数据</li>
        </ul>
        <h2>帮助文档</h2>
        <p>更多详细信息，请访问 <a href="https://docs.asktable.com/docs/integration/mcp/use-asktable-mcp">使用 MCP 访问 AskTable</a></p>
    </body>
    </html>
    """