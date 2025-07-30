import pytest
from fastmcp import Client
from pathlib import Path
import nest_asyncio

nest_asyncio.apply()


@pytest.mark.asyncio
async def test_subset_cells(mcp):
    # Pass the server directly to the Client constructor
    test_dir = Path(__file__).parent / "data/hg19"
    async with Client(mcp) as client:
        # First load the data
        result = await client.call_tool(
            "sc_io_read", {"request": {"filename": test_dir}, "adinfo": {}}
        )
        assert "AnnData" in result.content[0].text

        # Test filtering with min_genes parameter
        result = await client.call_tool(
            "sc_pp_subset_cells", {"request": {"min_genes": 200}}
        )
        assert "AnnData" in result.content[0].text

        result = await client.call_tool("sc_pp_calculate_qc_metrics", {"request": {}})
        assert "total_counts" in result.content[0].text
        result = await client.call_tool("sc_pp_log1p", {"request": {}})
        assert "log1p" in result.content[0].text

        result = await client.call_tool("sc_pp_normalize_total", {"request": {}})
        assert "log1p" in result.content[0].text

        result = await client.call_tool("sc_pp_highly_variable_genes", {"request": {}})
        assert "highly_variable" in result.content[0].text

        result = await client.call_tool("sc_tl_pca", {"request": {"n_comps": 50}})
        assert "X_pca" in result.content[0].text

        result = await client.call_tool(
            "sc_pp_neighbors", {"request": {}, "adinfo": {}}
        )
        assert "neighbors" in result.content[0].text
