import os
import inspect
from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.tools.tool_transform import ArgTransform
from ac_mcp_server.ac_client import ACMCPHttpClientAuth
import ac_mcp_server.tools as tools

mcp = FastMCP(
    name="ActiveCampaign",
    instructions="""
This server provides access to their data in ActiveCampaign, a marketing automation and CRM platform.
Customers may refer to ActiveCampagaign as AC. Provide guidance to the user but do not imply that you can take actions that you have not been given tools to do.
""",
    log_level="ERROR",
)


"""
Dynamically register tools, and provide a default auth from user environment variables.

This looks like overkill, but it allows us to mount these tools in the ac-agents repo directly.
Each system (FastAPI here, and PydanticAI in ac-agents) can hide the auth parameter from the LLM, 
and populate it with the information it has at hand.
"""


for name, func in inspect.getmembers(tools, inspect.isfunction):
    # Skip any internal or special methods
    if name.startswith("_"):
        continue

    mcp.add_tool(Tool.from_function(func, exclude_args=["auth"]))


def main():
    mcp.run()
