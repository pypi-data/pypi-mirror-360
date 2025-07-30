import pytest
from fastmcp import Client
import nest_asyncio

# Apply nest_asyncio at module level
nest_asyncio.apply()


@pytest.mark.asyncio
async def test_tool_selection(mcp):
    task = """
    read the file  /date/test.h5ad , filter the cells with ncells>100
    """
    async with Client(mcp) as client:
        result = await client.call_tool("auto_search_tool", {"task": task})
        assert "io_read" in result.content[0].text
