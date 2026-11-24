"""EarthWatch FastMCP read-only event tools."""
from fastmcp import FastMCP
from core import run

mcp=FastMCP("MUHRIS EarthWatch")
@mcp.tool
def browse_natural_events(keyword: str = "all") -> dict:
    """View current NASA/USGS public reports; no hazard predictions."""
    return run(keyword)

@mcp.tool
def recent_earthquakes() -> dict:
    """View USGS earthquake reports and source URLs."""
    return run("earthquake")

if __name__ == "__main__":
    mcp.run()
