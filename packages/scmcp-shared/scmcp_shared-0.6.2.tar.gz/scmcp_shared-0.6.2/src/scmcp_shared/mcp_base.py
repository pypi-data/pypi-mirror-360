import inspect
from fastmcp import FastMCP
from .schema import AdataInfo
from .util import filter_tools
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import asyncio
from typing import Optional, List, Any
from abcoder.backend import NotebookManager


# class BaseMCP:
#     """Base class for all Scanpy MCP classes."""

#     def __init__(self, name: str, instructions=None, lifespan=None, include_tools: list = None, exclude_tools: list = None, AdataInfo = AdataInfo):
#         """
#         Initialize BaseMCP with optional tool filtering.

#         Args:
#             name (str): Name of the MCP server
#             include_tools (list, optional): List of tool names to include. If None, all tools are included.
#             exclude_tools (list, optional): List of tool names to exclude. If None, no tools are excluded.
#             AdataInfo: The AdataInfo class to use for type annotations.
#         """
#         self.mcp = FastMCP(name, instructions=instructions, lifespan=lifespan)
#         self.include_tools = include_tools
#         self.exclude_tools = exclude_tools
#         self.AdataInfo = AdataInfo
#         self._register_tools()

#     def _register_tools(self):
#         """Register all tool methods with the FastMCP instance based on include/exclude filters"""
#         # Get all methods of the class
#         methods = inspect.getmembers(self, predicate=inspect.ismethod)

#         # Filter methods that start with _tool_
#         tool_methods = [tl_method() for name, tl_method in methods if name.startswith('_tool_')]

#         # Filter tools based on include/exclude lists
#         if self.include_tools is not None:
#             tool_methods = [tl for tl in tool_methods if tl.name in self.include_tools]

#         if self.exclude_tools is not None:
#             tool_methods = [tl for tl in tool_methods if tl.name not in self.exclude_tools]

#         # Register filtered tools
#         for tool in tool_methods:
#             # Get the function returned by the tool method
#             if tool is not None:
#                 self.mcp.add_tool(tool)


class BaseMCP:
    """Base class for all Scanpy MCP classes."""

    def __init__(
        self,
        name: str,
        include_tools: list = None,
        exclude_tools: list = None,
        AdataInfo=AdataInfo,
    ):
        """
        Initialize BaseMCP with optional tool filtering.

        Args:
            name (str): Name of the MCP server
            include_tools (list, optional): List of tool names to include. If None, all tools are included.
            exclude_tools (list, optional): List of tool names to exclude. If None, no tools are excluded.
            AdataInfo: The AdataInfo class to use for type annotations.
        """
        self.mcp = FastMCP(name)
        self.include_tools = include_tools
        self.exclude_tools = exclude_tools
        self.AdataInfo = AdataInfo
        self._register_tools()

    def _register_tools(self):
        """Register all tool methods with the FastMCP instance based on include/exclude filters"""
        # Get all methods of the class
        methods = inspect.getmembers(self, predicate=inspect.ismethod)

        # Filter methods that start with _tool_
        tool_methods = [
            tl_method() for name, tl_method in methods if name.startswith("_tool_")
        ]

        # Filter tools based on include/exclude lists
        if self.include_tools is not None:
            tool_methods = [tl for tl in tool_methods if tl.name in self.include_tools]

        if self.exclude_tools is not None:
            tool_methods = [
                tl for tl in tool_methods if tl.name not in self.exclude_tools
            ]

        # Register filtered tools
        for tool in tool_methods:
            # Get the function returned by the tool method
            if tool is not None:
                self.mcp.add_tool(tool)


class BaseMCPManager:
    """Base class for MCP module management."""

    def __init__(
        self,
        name: str,
        instructions: Optional[str] = None,
        include_modules: Optional[List[str]] = None,
        exclude_modules: Optional[List[str]] = None,
        include_tools: Optional[List[str]] = None,
        exclude_tools: Optional[List[str]] = None,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        backend: Optional[NotebookManager] = None,
    ):
        """
        Initialize BaseMCPManager with optional module filtering.

        Args:
            name (str): Name of the MCP server
            include_modules (List[str], optional): List of module names to include. If None, all modules are included.
            exclude_modules (List[str], optional): List of module names to exclude. If None, no modules are excluded.
            include_tools (List[str], optional): List of tool names to include. If None, all tools are included.
            exclude_tools (List[str], optional): List of tool names to exclude. If None, no tools are excluded.
        """
        self.exec_backend = backend()
        self.mcp = FastMCP(
            name,
            instructions=instructions,
            lifespan=self.exec_lifespan,
            include_tags=include_tags,
            exclude_tags=exclude_tags,
        )
        self.include_modules = include_modules
        self.exclude_modules = exclude_modules
        self.include_tools = include_tools
        self.exclude_tools = exclude_tools
        self.available_modules = {}
        self.init_mcp()
        self.register_mcp()

    def init_mcp(self):
        """Initialize available modules. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement init_mcp")

    def register_mcp(self):
        """Register modules based on include/exclude filters."""
        # Filter modules based on include/exclude lists
        if self.include_modules is not None:
            self.available_modules = {
                k: v
                for k, v in self.available_modules.items()
                if k in self.include_modules
            }

        if self.exclude_modules is not None:
            self.available_modules = {
                k: v
                for k, v in self.available_modules.items()
                if k not in self.exclude_modules
            }

        # Register each module
        for module_name, mcpi in self.available_modules.items():
            if isinstance(mcpi, FastMCP):
                if self.include_tools is not None and module_name in self.include_tools:
                    mcpi = filter_tools(
                        mcpi, include_tools=self.include_tools[module_name]
                    )
                if self.exclude_tools is not None and module_name in self.exclude_tools:
                    mcpi = filter_tools(
                        mcpi, exclude_tools=self.exclude_tools[module_name]
                    )

                asyncio.run(self.mcp.import_server(module_name, mcpi))
            else:
                asyncio.run(self.mcp.import_server(module_name, mcpi().mcp))

    @asynccontextmanager
    async def exec_lifespan(self, server: FastMCP) -> AsyncIterator[Any]:
        yield self.exec_backend
