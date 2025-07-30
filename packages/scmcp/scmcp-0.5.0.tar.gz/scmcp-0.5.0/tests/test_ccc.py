import pytest
from fastmcp import Client
from pathlib import Path

import nest_asyncio

nest_asyncio.apply()


@pytest.mark.asyncio
async def test_ls_ccc_method(mcp):
    """Test listing available CCC methods."""
    async with Client(mcp) as client:
        result = await client.call_tool("li_ccc_ls_ccc_method", {})
        assert isinstance(result.content[0].text, str)
        assert "cellphonedb" in result.content[0].text.lower()
        assert "cellchat" in result.content[0].text.lower()


@pytest.mark.asyncio
async def test_ccc_communicate(mcp):
    """Test cell-cell communication analysis with different methods."""
    test_dir = Path(__file__).parent / "data/pbmc68k_reduced.h5ad"

    async with Client(mcp) as client:
        # First read the data
        result = await client.call_tool(
            "sc_io_read", {"request": {"filename": test_dir}}
        )
        assert "AnnData" in result.content[0].text

        # Test cellphonedb method
        result = await client.call_tool(
            "li_ccc_communicate",
            {"request": {"method": "cellphonedb", "groupby": "bulk_labels"}},
        )
        assert "adata" in result.content[0].text

        # Test cellchat method
        result = await client.call_tool(
            "li_ccc_communicate",
            {"request": {"method": "cellchat", "groupby": "bulk_labels"}},
        )
        assert "adata" in result.content[0].text


@pytest.mark.asyncio
async def test_rank_aggregate(mcp):
    """Test rank aggregation of multiple CCC methods."""
    test_dir = Path(__file__).parent / "data/pbmc68k_reduced.h5ad"

    async with Client(mcp) as client:
        # First read the data
        result = await client.call_tool(
            "sc_io_read",
            {
                "request": {"filename": test_dir},
                "adinfo": {"sampleid": "pbmc68k", "adtype": "exp"},
            },
        )
        assert "AnnData" in result.content[0].text

        # Run rank aggregation
        result = await client.call_tool(
            "li_ccc_rank_aggregate",
            {
                "request": {
                    "methods": ["cellphonedb", "cellchat"],
                    "groupby": "bulk_labels",
                }
            },
        )
        assert "adata" in result.content[0].text
