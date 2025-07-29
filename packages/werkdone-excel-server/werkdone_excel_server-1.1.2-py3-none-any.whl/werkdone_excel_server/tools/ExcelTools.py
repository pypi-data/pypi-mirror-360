from pathlib import Path
from smolagents import Tool
from typing import Dict, List
import os
from .workbook import create_workbook, create_sheet, get_or_create_workbook
from .data import write_data
from .exceptions import WorkbookError, DataError
import datetime

DOWNLOAD_DIR = Path(__file__).resolve().parent.parent / "downloads"

class DirectExcelTool(Tool):
    name = "write_excel_file"
    description = "Write data to an Excel file with multiple sheets"
    inputs = {
        "filepath": {"type": "string", "description": "Full path to the Excel file"},
        "data": {"type": "object", "description": "Dictionary with sheet names as keys and data as list of lists"},
    }
    output_type = "string"

    def forward(self, filepath: str, data: Dict[str, List[List]]) -> str:
        try:
            # Return early if inputs are incomplete (intermediate or malformed call)
            if not filepath or not data:
                return "⚠️ Skipped tool call: 'filepath' and 'data' must both be provided."
    
            path = Path(filepath)

            # Check if only filename or relative path was given
            if not path.is_absolute():
                path = DOWNLOAD_DIR / path

            # If it's a directory or has no valid extension, make a unique file
            if path.is_dir() or not str(path).endswith((".xlsx", ".xlsm", ".xltx", ".xltm")):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                path = path / f"visitation_{timestamp}.xlsx"

            filepath = str(path)
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Create workbook if it doesn't exist
            if not Path(filepath).exists():
                # Just create the workbook with first sheet name (if any)
                first_sheet = list(data.keys())[0] if data else "Sheet1"
                create_workbook(filepath, first_sheet)

            wb = get_or_create_workbook(filepath)
            existing_sheets = wb.sheetnames
            wb.close() 

            # Write data to each sheet
            for sheet_name, rows in data.items():
                if not rows or not isinstance(rows, list) or not all(isinstance(row, list) for row in rows):
                    raise ValueError(f"Invalid or empty data format for sheet: '{sheet_name}'")

                # Create sheet if it doesn't exist
                if sheet_name not in existing_sheets:
                    try:
                        create_sheet(filepath, sheet_name)
                    except WorkbookError as e:
                        # If sheet already exists due to race condition, ignore
                        if "already exists" not in str(e):
                            raise

                # Write data to the sheet
                write_data(filepath, sheet_name, rows, start_cell="A1")

            file_size = Path(filepath).stat().st_size
            return f"✅ Excel file written to `{filepath}` with {len(data)} sheet(s) ({file_size} bytes)"
        
        except (WorkbookError, DataError, ValueError) as e:
            return f"❌ Excel write failed: {str(e)}"
        except Exception as e:
            return f"❌ Unexpected error: {str(e)}"
