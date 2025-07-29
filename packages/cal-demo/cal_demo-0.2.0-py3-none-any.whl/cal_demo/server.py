import requests
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("TestNG Case Generator")


@mcp.tool()
def say_hello(content: str) -> str:
    """
    参数：
    - content: 要传递的消息内容
    当别人输入的时候，给别人打招呼，say hello
    """
    return content + "hello,hahaha!"
def run():
    mcp.run(transport='stdio')
if __name__ == '__main__':
   run()
