# server.py
from mcp.server.fastmcp import FastMCP
from werkdone_excel_server.tools.ExcelTools import DirectExcelTool

# register excel mcp server
mcp = FastMCP("excel-mcp-server")

# wrap the excel tool using the @mcp.tool decorator
@mcp.tool()
def write_excel_file(filepath: str, data: dict) -> str:
    """
    Write structured tabular data to an Excel (.xlsx) file, organized by sheets.

    This tool is typically used in conjunction with data retrieved from the 
    `vms_mcp_server`, such as visitation lists or summaries. The `data` argument
    should be a dictionary mapping sheet names (str) to a list of rows, where each 
    row is itself a list of cell values (e.g. strings, numbers, dates).

    Args:
        filepath: Absolute or relative path to the output Excel file. If a relative 
                  path is given, it will be saved under the `downloads/` folder 
                  of the Excel MCP server. If the directory does not exist, it 
                  will be created automatically.
        data: A dictionary of sheet data, structured as:
            {
              "Sheet1": [
                  ["Header1", "Header2", "Header3"],
                  ["Row1Col1", "Row1Col2", "Row1Col3"],
                  ...
              ],
              "Sheet2": [
                  ...
              ]
            }

    Returns:
        A string describing the result of the operation, including file path, number
        of sheets written, and file size. If invalid input is passed, a warning will
        be returned instead.

    Example:
        write_excel_file(
            filepath="downloads/august_report.xlsx",
            data={
                "visitations": [
                    ["Id", "Visitor", "Date", "Time"],
                    ["abc123", "Goku", "2024-08-01", "09:00 AM"]
                ]
            }
        )

    Notes:
        - This tool requires both `filepath` and `data` to be present.
        - If the Excel file doesn't exist, it will be created.
        - If a sheet doesn't exist, it will be created.
        - If `data` is malformed, the tool will return an error message.
    """
    if not filepath or not data:
        return "⚠️ Skipped tool call: 'filepath' and 'data' must both be provided.'"
 
    return DirectExcelTool().forward(filepath, data)

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()