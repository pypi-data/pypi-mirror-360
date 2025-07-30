import pytest
from scmcp_shared.backend import AdataManager
from scmcp_shared.mcp_base import BaseMCPManager
from scmcp_shared.server.preset import ScanpyIOMCP
from scmcp_shared.server.preset import ScanpyPreprocessingMCP
from scmcp_shared.server.preset import ScanpyToolsMCP
from scmcp_shared.server.preset import ScanpyPlottingMCP
from scmcp_shared.server.preset import ScanpyUtilMCP
from scmcp_shared.server.auto import auto_mcp


class ScanpyMCPManager(BaseMCPManager):
    """Manager class for Scanpy MCP modules."""

    def init_mcp(self):
        """Initialize available Scanpy MCP modules."""
        self.available_modules = {
            "io": ScanpyIOMCP().mcp,
            "pp": ScanpyPreprocessingMCP().mcp,
            "tl": ScanpyToolsMCP().mcp,
            "pl": ScanpyPlottingMCP().mcp,
            "ul": ScanpyUtilMCP().mcp,
            "auto": auto_mcp,
        }


@pytest.fixture
def mcp():
    return ScanpyMCPManager("scmcp", backend=AdataManager).mcp
