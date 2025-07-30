import argparse
import os
from fastmcp import FastMCP

from asktable_mcp_server.at_apis import (
    get_asktable_answer,
    get_asktable_sql,
)
from asktable_mcp_server.sse_server import main as sse_main
from asktable_mcp_server.schemas import (
    QuestionParamQuery,
    QuestionParamGenSQL,
    RoleIdParam,
    RoleVariablesParam,
    GEN_SQL_DESCRIPTION,
    QUERY_DESCRIPTION,
)

mcp = FastMCP(name="Asktable stdio mcp server running...")


@mcp.tool(name='使用 AskTable 查询数据')
async def query(
    question: QuestionParamQuery,
    role_id: RoleIdParam = None,
    role_variables: RoleVariablesParam = None
) -> dict:
    """
    {description}
    """.format(description=QUERY_DESCRIPTION)
    # 构建基本参数
    params = {
        "api_key": os.getenv("API_KEY"),
        "datasource_id": os.getenv("DATASOURCE_ID"),
        "question": question,
        "base_url": os.getenv("BASE_URL") or None,
        "role_id": role_id,
        "role_variables": role_variables,
    }

    # 调用API获取数据
    message = await get_asktable_answer(**params)
    return message


@mcp.tool(name='使用 AskTable 生成 SQL')
async def gen_sql(
    question: QuestionParamGenSQL,
    role_id: RoleIdParam = None,
    role_variables: RoleVariablesParam = None
) -> dict:
    """
    {description}
    """.format(description=GEN_SQL_DESCRIPTION)
    # 构建基本参数
    params = {
        "api_key": os.getenv("API_KEY"),
        "datasource_id": os.getenv("DATASOURCE_ID"),
        "question": question,
        "base_url": os.getenv("BASE_URL") or None,
        "role_id": role_id,
        "role_variables": role_variables,
    }

    # 调用API获取SQL
    message = await get_asktable_sql(**params)
    return message


def main():
    # 创建参数解析器
    parser = argparse.ArgumentParser(description="Asktable MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="选择通信协议: stdio或sse",
    )
    parser.add_argument("--port", type=int, default=8095, help="SSE模式使用的端口号")
    parser.add_argument(
        "--path_prefix",
        type=str,
        default="",
        help="路径前缀，用于在反向代理环境中设置正确的路径（如：/mcp）",
    )
    parser.add_argument(
        "--base_url",
        type=str,
        default=None,
        help="请求所用的AskTable API地址，填写了则使用指定服务器地址，否则使用默认的AskTable API地址",
    )
    args = parser.parse_args()

    # 根据参数启动不同协议
    if args.transport == "stdio":
        mcp.run(transport="stdio")  # 保持原有stdio模式
    else:
        # SSE模式需要额外配置
        sse_main(
            port=args.port,
            base_url=args.base_url,
            path_prefix=args.path_prefix,
        )


if __name__ == "__main__":
    main()
