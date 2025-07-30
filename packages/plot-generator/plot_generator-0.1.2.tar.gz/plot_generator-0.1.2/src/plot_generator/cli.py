import click
from .server import main

@click.command()
@click.option("--transport", type=click.Choice(["stdio", "http", "sse"]),
              default="stdio", show_default=True,
              help="FastMCP transport to use")
def cli(transport: str):
    """Run plot-generator MCP server."""
    if transport != "sse":
        # scheme change at runtime
        from mcp.server.fastmcp import FastMCP
        from .server import mcp
        mcp.run(transport=transport)
    else:
        main()

if __name__ == "__main__":
    cli()