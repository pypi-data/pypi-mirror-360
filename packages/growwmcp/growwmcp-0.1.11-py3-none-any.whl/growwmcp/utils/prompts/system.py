from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent
import yaml
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from ..prompt_lib import system_instructions
from jinja2 import Template

mcp = FastMCP(name="PromptServer")


@mcp.prompt()
def system_prompt() -> str:
    return Template(system_instructions).render(
        CURRENT_DATETIME=datetime.now(tz=ZoneInfo("Asia/Kolkata")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


if __name__ == "__main__":
    print(system_prompt())
