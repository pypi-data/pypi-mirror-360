from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message, PromptMessage, TextContent
import yaml
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from ..prompt import sys_prompt

mcp = FastMCP(name="PromptServer")


@mcp.prompt()
def template_prompt() -> str:

    # Combine all sections into a comprehensive system prompt
    combined_prompt = sys_prompt.replace(
        "$CURRENT_TIME$",
        datetime.now(tz=ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S"),
    )

    return combined_prompt.strip()


# @mcp.prompt()
# def get_full_instructions() -> PromptMessage:
#     """Returns comprehensive instructions as a structured prompt message"""

#     with open('prompt.yaml', "r") as f:
#         prompt = yaml.safe_load(f)

#     # Create a more structured prompt message
#     combined_prompt = f"""
# {prompt["sys_prompt"]}

# ## Additional Guidelines:

# ### UI Design Instructions:
# {prompt["ui_design"]}

# ### Data Analysis Instructions:
# {prompt["data_views"]}

# ### Stock Data Handling:
# {prompt["stock_data"]}

# Remember to always follow these instructions when responding to user queries. Your behavior should strictly adhere to these guidelines.
# """

#     return PromptMessage(
#         messages=[
#             Message(
#                 role="system",
#                 content=TextContent(text=combined_prompt.strip())
#             )
#         ]
#     )


if __name__ == "__main__":
    print(template_prompt())
