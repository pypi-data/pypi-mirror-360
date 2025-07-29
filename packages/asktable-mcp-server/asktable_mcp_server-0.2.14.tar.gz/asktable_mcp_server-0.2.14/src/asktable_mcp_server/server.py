import argparse
import logging
import os

from fastmcp import FastMCP

from asktable_mcp_server.tools import (
    get_asktable_data,
    get_asktable_sql,
    get_datasources_info,
)
from asktable_mcp_server.sse_server import main as sse_main

mcp = FastMCP(name="Asktable stdio mcp server running...")


@mcp.tool(name='使用 AskTable 生成 SQL')
async def gen_sql(query: str) -> str:
    """
    根据用户查询生成对应的SQL语句
    不需要指定数据源ID，该函数已在内部指定了数据源ID，直接发起请求即可
    该函数将用户的查询转换为SQL语句，仅返回SQL文本，不执行查询。

    :param query: 用户的查询内容
                  示例：
                  - "我需要查询昨天的订单总金额的sql"
                  - "我要找出销售额前10的产品的sql"
                  - "统计每个部门的员工数量的sql"
    :return: 生成的SQL语句字符串

    使用场景：
        - 需要查看生成的SQL语句
        - 需要将自然语言转化为SQL查询
        - 仅需要SQL文本而不需要执行结果
    """
    # 构建基本参数
    params = {
        "api_key": os.getenv("API_KEY"),
        "datasource_id": os.getenv("DATASOURCE_ID"), 
        "question": query,
        "base_url": os.getenv("BASE_URL") or None,
    }
    
    # 调用API获取SQL
    message = await get_asktable_sql(**params)
    return message


@mcp.tool(name='使用 AskTable 查询数据')
async def query(query: str) -> str:
    """
    根据用户的问题，直接返回数据结果
    不需要指定数据源ID，该函数已在内部指定了数据源ID，直接发起请求即可
    该函数执行用户的查询并返回实际的数据结果或答案，而不是SQL语句。

    :param query: 用户的查询内容
                  示例：
                  - "昨天的订单总金额是多少"
                  - "列出销售额前10的产品"
                  - "每个部门有多少员工"
    :return: 查询的实际结果

    使用场景：
        - 需要直接获取查询答案
        - 搜索数据库数据
        - 需要查看实际数据结果
        - 不关心SQL细节，只要最终答案与结论
    """
    # 构建基本参数
    params = {
        "api_key": os.getenv("API_KEY"),
        "datasource_id": os.getenv("DATASOURCE_ID"),
        "question": query,
        "base_url": os.getenv("BASE_URL") or None,
    }

    # 调用API获取数据
    message = await get_asktable_data(**params)
    return message


@mcp.tool(name='列出 AskTable 中的所有数据')
async def list_data() -> str:
    """
    获取当前用户apikey下的可用的所有数据库（数据源）信息

    该函数会自动获取当前用户有权限访问的全部数据源，并返回每个数据源的关键信息，包括数据源ID、推理引擎类型和数据库描述。

    :return: 如果该用户的数据库有表的话，会返回数据源信息列表，每个元素为字典，包含以下字段：
        - datasource_id: 数据源唯一ID
        - 数据库引擎: 数据源的推理引擎类型（如：mysql、excel、postgresql等）
        - 数据库描述: 数据源的详细描述信息

            如果该用户的数据库中没有表，则返回"[目前该用户的数据库中还没有数据]"
    示例返回值:
    example1 - 对应数据库中有表的情况:
        [
            {
                "datasource_id": "ds_6iewvP4cpSyhO76P2Tv8MW",
                "数据库引擎": "mysql",
                "数据库描述": "包含大学的课程、教授、学生、部门、奖项、宿舍管理、考试成绩等信息的综合数据库。"
            },
            {
                "datasource_id": "ds_43haVWseJhEizg2GHbErMu",
                "数据库引擎": "excel",
                "数据库描述": "包含各省份的经济指标与电信行业相关数据，帮助分析区域经济与电信发展的关系。"
            },
            {
                "datasource_id": "ds_2Ds3Ude2MkYa3FAWvyVSRG",
                "数据库引擎": "mysql",
                "数据库描述": "该数据库用于管理基金销售相关信息，包括订单、产品和销售员等数据表。"
            }
        ]

    example2 - 对应数据库中没有表的情况:
        “该用户还没有创建任何数据库”

    使用场景：
        - 用户需要查看自己有哪些数据库，获取这些数据库的datasource_id、该数据库所用的数据库引擎和描述信息，以供后续需要。
    """
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL") or None

    result = await get_datasources_info(
        api_key=api_key, base_url=base_url
    )
    logging.info(result["status"])
    return result["data"]


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
