import pytest
from fastmcp import Client
from pathlib import Path
import nest_asyncio

nest_asyncio.apply()


@pytest.mark.asyncio
async def test_read_and_write(mcp):
    test_dir = Path(__file__).parent / "data/hg19"
    outfile = Path(__file__).parent / "data/test.h5ad"
    async with Client(mcp) as client:
        # tools = await client.list_tools()
        result = await client.call_tool(
            "sc_io_read", {"request": {"filename": test_dir}}
        )
        assert "AnnData" in result.content[0].text

        result = await client.call_tool(
            "sc_io_write", {"request": {"filename": outfile}}
        )
        assert outfile.exists()
        outfile.unlink()
