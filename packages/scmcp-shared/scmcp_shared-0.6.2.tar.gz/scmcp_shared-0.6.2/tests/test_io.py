import pytest
from fastmcp import Client
from pathlib import Path
import nest_asyncio

# Apply nest_asyncio at module level
nest_asyncio.apply()


@pytest.mark.asyncio
async def test_read_and_write(mcp):
    # Pass the server directly to the Client constructor
    test_dir = Path(__file__).parent / "data/hg19"
    outfile = Path(__file__).parent / "data/test.h5ad"
    async with Client(mcp) as client:
        # tools = await client.list_tools()
        # client._tools = tools
        result = await client.call_tool("io_read", {"request": {"filename": test_dir}})
        print(result)
        assert "AnnData" in result.content[0].text

        result = await client.call_tool("io_write", {"request": {"filename": outfile}})
        assert outfile.exists()
        outfile.unlink()
