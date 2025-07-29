
import asyncio
import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
import fastmcp

from asktable_mcp_server.tools import (
    get_asktable_data,
    get_asktable_sql,
    get_datasources_info,
)
from asktable_mcp_server.version import __version__

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 全局变量
server_ready = False
mcp = None  # 将在 main 函数中初始化


@asynccontextmanager
async def lifespan(fastmcp_instance):
    """服务器启动和关闭的生命周期管理"""
    global server_ready

    # 启动逻辑
    logger.info("服务器正在初始化...")

    await asyncio.sleep(2)

    server_ready = True
    logger.info("服务器初始化完成，准备接受请求")

    yield  # 服务器运行期间

    # 关闭逻辑
    logger.info("服务器正在关闭...")
    server_ready = False


def create_mcp_server(path_prefix: str = "", base_url: str = None):
    """创建 MCP 服务器实例"""
    global mcp

    
    # 创建服务器时传入 lifespan
    mcp = FastMCP(
        name="AskTable SSE MCP Server",
        lifespan=lifespan,
    )

    @mcp.custom_route(path_prefix + "/health", methods=["GET"])
    async def health_check(request: Request):
        """Health check endpoint to verify server is ready"""
        if not server_ready:
            return JSONResponse({"status": "initializing", "message": "Server is still initializing"})
        return JSONResponse({"status": "ready", "message": "Server is initialized and ready"})

    @mcp.custom_route(path_prefix + "/", methods=["GET"])
    async def home(request: Request):
        """Welcome page with configuration example"""
        # 从请求中获取主机名
        host = request.headers.get("host", "your-asktable-server-host") 
        scheme = request.url.scheme
        base_url = f"{scheme}://{host}"
        
        content = f"""
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
            <p>当前版本: v{__version__}</p>

            <h2>配置示例</h2>
            <p>在您的 Agent 配置文件中，添加以下配置:</p>
            <pre><code>{{
    "mcpServers": {{
        "asktable": {{
            "type": "sse",
            "url": "{base_url}{path_prefix}/sse/?apikey=YOUR_API_KEY&datasource_id=YOUR_DATASOURCE_ID",
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
        </body>
        </html>
        """
        return HTMLResponse(content=content)

    @mcp.tool(name="使用 AskTable 生成 SQL")
    async def gen_sql(question: str) -> str:
        """
        根据用户查询生成对应的SQL语句
        不需要指定数据源ID，该函数已在内部指定了数据源ID，直接发起请求即可
        该函数将用户的查询转换为SQL语句，仅返回SQL文本，不执行查询。

        :param question: 用户的查询内容
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
        global server_ready

        if not server_ready:
            return "Server is still initializing, please wait"

        request = get_http_request()
        api_key = request.query_params.get("apikey", None)
        datasource_id = request.query_params.get("datasource_id", None)

        logging.info(f"api_key:{api_key}")
        logging.info(f"datasource_id:{datasource_id}")

        params = {
            "api_key": api_key,
            "datasource_id": datasource_id,
            "question": question,
            "base_url": base_url,
        }

        message = await get_asktable_sql(**params)
        return message

    @mcp.tool(name="使用 AskTable 查询数据")
    async def query(question: str) -> str:
        """
        根据用户的问题，直接返回数据结果
        不需要指定数据源ID，该函数已在内部指定了数据源ID，直接发起请求即可
        该函数执行用户的查询并返回实际的数据结果或答案，而不是SQL语句。

        :param question: 用户的查询内容
                      示例：
                      - "昨天的订单总金额是多少"
                      - "列出销售额前10的产品"
                      - "每个部门有多少员工"
        :return: 查询的实际结果

        使用场景：
            - 需要直接获取查询答案
            - 搜索数据库数据
            - 需要查看实际数据结果
            - 不需要SQL细节，只要最终答案与结论
        """
        global server_ready

        if not server_ready:
            return "Server is still initializing, please wait"

        request = get_http_request()
        api_key = request.query_params.get("apikey", None)
        datasource_id = request.query_params.get("datasource_id", None)

        params = {
            "api_key": api_key,
            "datasource_id": datasource_id,
            "question": question,
            "base_url": base_url,
        }

        message = await get_asktable_data(**params)
        return message

    @mcp.tool(name="列出 AskTable 中的所有数据")
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
            "该用户还没有创建任何数据库"

        使用场景：
            - 用户需要查看自己有哪些数据库，获取这些数据库的datasource_id、该数据库所用的数据库引擎和描述信息，以供后续需要。
        """
        global server_ready

        if not server_ready:
            return "Server is still initializing, please wait"

        request = get_http_request()
        api_key = request.query_params.get("apikey", None)

        result = await get_datasources_info(api_key=api_key, base_url=base_url)
        logging.info(result)
        return result["data"]

    return mcp


def main(base_url: str = None, path_prefix: str = "", port: int = 8095):
    """
    启动 SSE 服务器的主函数
    
    :param base_url: 请求所用的服务器主机地址，填写了则使用指定服务器地址，否则使用默认的AskTable服务地址
    :param path_prefix: 路径前缀，用于在反向代理环境中设置正确的路径（如：/mcp）
    :param port: 服务器端口号
    """
    global mcp

    fastmcp.settings.sse_path = path_prefix + "/sse/"
    fastmcp.settings.message_path = path_prefix + "/messages/"
    
    # 创建 MCP 服务器实例
    mcp = create_mcp_server(path_prefix=path_prefix, base_url=base_url)
    
    # 记录配置信息
    logger.info("启动 SSE 服务器")
    logger.info(f"base_url: {base_url}")
    logger.info(f"path_prefix: {path_prefix}")
    logger.info(f"port: {port}")


    # 启动服务器
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=port,
        path=fastmcp.settings.sse_path,
    )


if __name__ == "__main__":
    print("Please use the server.py file to start the SSE server")
