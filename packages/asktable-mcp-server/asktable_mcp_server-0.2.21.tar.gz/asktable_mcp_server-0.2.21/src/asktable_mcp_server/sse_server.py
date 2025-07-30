
import asyncio
import logging
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
import fastmcp

from asktable_mcp_server.at_apis import (
    get_asktable_answer,
    get_asktable_sql,
)
from asktable_mcp_server.version import __version__
from asktable_mcp_server.schemas import (
    QuestionParamQuery,
    QuestionParamGenSQL,
    RoleIdParam,
    RoleVariablesParam,
    GEN_SQL_DESCRIPTION,
    QUERY_DESCRIPTION,
    get_home_page_html,
)

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
        
        content = get_home_page_html(__version__, base_url, path_prefix)
        return HTMLResponse(content=content)

    @mcp.tool(name="使用 AskTable 查询数据")
    async def query(
        question: QuestionParamQuery,
        role_id: RoleIdParam = None,
        role_variables: RoleVariablesParam = None
    ) -> dict:
        """
        {description}
        """.format(description=QUERY_DESCRIPTION)
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
            "role_id": role_id,
            "role_variables": role_variables,
        }

        message = await get_asktable_answer(**params)
        return message
    
    @mcp.tool(name="使用 AskTable 生成 SQL")
    async def gen_sql(
        question: QuestionParamGenSQL,
        role_id: RoleIdParam = None,
        role_variables: RoleVariablesParam = None
    ) -> dict:
        """
        {description}
        """.format(description=GEN_SQL_DESCRIPTION)
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
            "role_id": role_id,
            "role_variables": role_variables,
        }

        message = await get_asktable_sql(**params)
        return message

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
