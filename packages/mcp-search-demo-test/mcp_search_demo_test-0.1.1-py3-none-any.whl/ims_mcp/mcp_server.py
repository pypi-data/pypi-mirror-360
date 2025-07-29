import os
import json
from mcp.server.fastmcp import FastMCP
from alibabacloud_ice20201109.client import Client as ICE20201109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ice20201109 import models as ice20201109_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient
import logging
from dotenv import load_dotenv
import asyncio
import sys

logging.basicConfig(level=logging.INFO)


def create_new_mcp_server():
    # Create an MCP server
    mcp = FastMCP("Media Search MCP")

    ice_client = create_client()

    @mcp.tool()
    def media_search(text: str) -> str:
        """该工具主要是根据输入的搜索词text，搜索相应搜索库中有关的视频信息，并返回相关视频信息列表，包含MediaId和ClipInfo等。

        Args:
            text (string): 搜索词
        """

        result = search_media_by_hybrid(text)
        return result

    def search_media_by_hybrid(text: str) -> str:
        search_media_by_hybrid_request = ice20201109_models.SearchMediaByHybridRequest(
            text=text
        )
        runtime = util_models.RuntimeOptions()
        try:
            # 复制代码运行请自行打印 API 的返回值
            resp = ice_client.search_media_by_hybrid_with_options(search_media_by_hybrid_request, runtime)
            print(resp.body)
            dict_list = [item.to_map() for item in resp.body.media_list]
            json_str = json.dumps(dict_list, ensure_ascii=False)
            return json_str
        except Exception as error:
            # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
            # 错误 message
            print(error.message)
            # 诊断地址
            print(error.data.get("Recommend"))
            UtilClient.assert_as_string(error.message)
        return "media search failed."

    return mcp


def create_client() -> ICE20201109Client:
    access_key_id = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
    access_key_secret = os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
    security_token = os.getenv('ALIBABA_CLOUD_SECURITY_TOKEN')
    region = os.getenv('ALIBABA_CLOUD_REGION')

    config = open_api_models.Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        security_token=security_token,
    )

    config.endpoint = f'ice.{region}.aliyuncs.com'
    return ICE20201109Client(config)


def main():
    """命令行入口点，用于启动 IMS Video Editing MCP 服务器"""
    # 加载环境变量
    load_dotenv()

    try:
        # 创建MCP服务器
        mcp = create_new_mcp_server()
        print("start mcp server")
        asyncio.run(mcp.run())
    except Exception as e:
        print(f"启动服务器时出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()