from .server import mcp
from .tools import csv_tools




def main() -> None:
    print("Hello from exchange-rate-mcp!")
    mcp.run(transport="stdio")
