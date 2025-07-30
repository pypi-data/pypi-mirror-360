import pytest
from fastmcp import Client
from pathlib import Path

import nest_asyncio

nest_asyncio.apply()


@pytest.mark.asyncio
async def test_activity(mcp):
    testfile = Path(__file__).parent / "data/pbmc3k_processed.h5ad"
    # outfile = Path(__file__).parent / "data/test.h5ad"
    async with Client(mcp) as client:
        result = await client.call_tool(
            "sc_io_read",
            {
                "request": {"filename": testfile},
                "adinfo": {"sampleid": "pbmc3k", "adtype": "exp"},
            },
        )
        assert "AnnData" in result.content[0].text

        result = await client.call_tool(
            "dc_if_pathway_activity",
            {
                "request": {"top": 500},
                "adinfo": {"sampleid": "pbmc3k", "adtype": "exp"},
            },
        )
        assert "score_mlm" in result.content[0].text

        result = await client.call_tool(
            "dc_if_tf_activity",
            {"request": {}, "adinfo": {"sampleid": "pbmc3k", "adtype": "exp"}},
        )
        assert "score_ulm" in result.content[0].text
