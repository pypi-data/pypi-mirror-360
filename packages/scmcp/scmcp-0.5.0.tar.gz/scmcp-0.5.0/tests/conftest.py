import pytest


@pytest.fixture
def mcp():
    from scmcp.server import SCMCPManager
    from scmcp_shared.backend import AdataManager

    mcp = SCMCPManager("scmcp", backend=AdataManager).mcp
    return mcp
