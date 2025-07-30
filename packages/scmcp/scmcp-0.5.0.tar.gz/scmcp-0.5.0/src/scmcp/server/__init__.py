from decoupler_mcp.server import DecouplerMCPManager
from liana_mcp.server import LianaMCPManager
from scanpy_mcp.server import ScanpyMCPManager
from scmcp_shared.mcp_base import BaseMCPManager
from infercnv_mcp.server import InferCNVMCPManager
from scmcp_shared.server.auto import auto_mcp
from scmcp_shared.backend import AdataManager
from scmcp_shared.server.code import nb_mcp
from scmcp_shared.server.rag import rag_mcp
from cellrank_mcp.server import CellrankMCPManager

sc_mcp = ScanpyMCPManager(
    "scanpy-mcp",
    backend=AdataManager,
    exclude_modules=["auto", "nb"],
    exclude_tools={
        "auto": ["search_tool", "run_tool"],
    },
).mcp

cr_mcp = CellrankMCPManager(
    "cellrank-mcp",
    include_modules=["pp", "kernel", "estimator", "pl"],
    include_tools={
        "pp": ["filter_and_normalize"],
        "pl": ["kernel_projection", "circular_projection"],
    },
    exclude_modules=["auto"],
    exclude_tools={
        "auto": ["search_tool", "run_tool"],
    },
    backend=AdataManager,
).mcp
dc_mcp = DecouplerMCPManager(
    "decoupler-mcp",
    include_modules=["if"],
    exclude_modules=["auto"],
    exclude_tools={
        "auto": ["search_tool", "run_tool"],
    },
    backend=AdataManager,
).mcp
cnv_mcp = InferCNVMCPManager(
    "infercnv-mcp",
    include_modules=["tl", "pl", "ul"],
    exclude_modules=["auto"],
    include_tools={
        "pl": ["chromosome_heatmap"],
        "tl": ["infercnv", "cnv_score"],
        "ul": ["load_gene_position"],
    },
    exclude_tools={
        "auto": ["search_tool", "run_tool"],
    },
    backend=AdataManager,
).mcp

li_mcp = LianaMCPManager(
    "liana-mcp",
    include_modules=["ccc", "pl"],
    exclude_modules=["auto"],
    include_tools={
        "ccc": ["communicate", "rank_aggregate", "ls_ccc_method"],
        "pl": ["ccc_dotplot", "circle_plot"],
    },
    exclude_tools={
        "auto": ["search_tool", "run_tool"],
    },
    backend=AdataManager,
).mcp


available_modules = {
    "sc": sc_mcp,
    "li": li_mcp,
    "cr": cr_mcp,
    "dc": dc_mcp,
    "cnv": cnv_mcp,
    "auto": auto_mcp,
    "nb": nb_mcp,
    "rag": rag_mcp,
}


class SCMCPManager(BaseMCPManager):
    """Manager class for SCMCP modules."""

    def init_mcp(self):
        """Initialize available SCMCP modules."""
        self.available_modules = available_modules
