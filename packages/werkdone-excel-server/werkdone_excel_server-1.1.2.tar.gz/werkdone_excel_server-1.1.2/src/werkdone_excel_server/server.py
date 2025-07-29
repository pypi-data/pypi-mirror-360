# server.py
from mcp.server.fastmcp import FastMCP
from werkdone_excel_server.tools.ExcelTools import DirectExcelTool

# register excel mcp server
mcp = FastMCP("excel-mcp-server")

# wrap the excel tool using the @mcp.tool decorator
@mcp.tool()
def write_excel_file(filepath: str, data: dict) -> str:
    """
    Write structured data to an Excel file with multiple sheets. 
    """
    return DirectExcelTool().forward(filepath, data)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()