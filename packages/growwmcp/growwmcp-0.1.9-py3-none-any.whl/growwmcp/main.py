from .utils.tools.portfolio import mcp as portfolio
from .utils.tools.utils import mcp as utils
from .utils.tools.orders import mcp as orders
from .utils.tools.instruments import mcp as instruments
from .utils.tools.margins import mcp as margins
from .utils.tools.livedata import mcp as livedata
from .utils.tools.historicaldata import mcp as historicaldata
from .utils.tools.feed import mcp as feed
from .utils.prompts.sysprompt_mcp import mcp as sysprompt
from .utils.tools.pattern import mcp as pattern
from fastmcp import FastMCP
import yaml
import os
import argparse
import json
from .utils.helper import load_system_instructions, LoggingMiddleware


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test", action="store_true", help="Run in test mode on port 8892"
    )
    parser.add_argument("--stdio", action="store_true", help="Run with stdio transport")
    parser.add_argument(
        "--demo1", action="store_true", help="Run in demo1 mode on port 8893"
    )
    parser.add_argument(
        "--demo2", action="store_true", help="Run in demo2 mode on port 8894"
    )
    args = parser.parse_args()

    mcp = FastMCP(
        name="Groww MCP Server",
        instructions=load_system_instructions(),
    )

    mcp.mount(prefix="portfolio", server=portfolio)
    mcp.mount(prefix="utils", server=utils)
    mcp.mount(prefix="orders", server=orders)
    mcp.mount(prefix="instruments", server=instruments)
    mcp.mount(prefix="margins", server=margins)
    mcp.mount(prefix="livedata", server=livedata)
    mcp.mount(prefix="historicaldata", server=historicaldata)
    mcp.mount(prefix="feed", server=feed)
    mcp.mount(prefix="prompt", server=sysprompt)
    mcp.mount(prefix="pattern", server=pattern)

    # mcp.add_middleware(LoggingMiddleware())
    if args.stdio:
        mcp.run(transport="stdio")
    elif args.test:
        mcp.run(transport="sse", host="0.0.0.0", port=8892)
    elif args.demo1:
        mcp.run(transport="sse", host="0.0.0.0", port=8893)
    elif args.demo2:
        mcp.run(transport="sse", host="0.0.0.0", port=8894)
    else:
        mcp.run(transport="sse", host="0.0.0.0", port=8891)


if __name__ == "__main__":
    main()
