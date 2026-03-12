import sys
import json
import os

from ai.sql_generator import generate_sql
from ai.sql_validator import validate_sql
from db.executor import execute_query

# Auto-install openpyxl if needed
try:
    import openpyxl
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=/tmp/pylib", "openpyxl"])
    sys.path.insert(0, "/tmp/pylib")
    import openpyxl

EXCEL_THRESHOLD = 100
EXCEL_OUTPUT_PATH = "/tmp/query_result.xlsx"

question = " ".join(sys.argv[1:])

# Step 1: Generate SQL from natural language
sql = generate_sql(question)

# Step 2: Safety validation
validate_sql(sql)

# Step 3: Execute query
result = execute_query(sql)

# Step 4: Output — export to Excel if > 100 rows, otherwise JSON
if len(result) > EXCEL_THRESHOLD:
    # Export to Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Query Result"

    # Header row
    if result:
        headers = list(result[0].keys())
        ws.append(headers)

        # Data rows
        for row in result:
            ws.append([row.get(h) for h in headers])

        # Auto-width columns
        for col_idx, header in enumerate(headers, 1):
            max_len = len(str(header))
            for row in result[:50]:  # sample first 50 rows for width
                cell_len = len(str(row.get(header, "")))
                if cell_len > max_len:
                    max_len = cell_len
            ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = min(max_len + 2, 50)

    wb.save(EXCEL_OUTPUT_PATH)

    print(json.dumps({
        "sql": sql,
        "total_rows": len(result),
        "export": "excel",
        "file_path": EXCEL_OUTPUT_PATH,
        "message": f"ผลลัพธ์มี {len(result)} รายการ ส่งออกเป็นไฟล์ Excel แล้วที่ {EXCEL_OUTPUT_PATH}"
    }, indent=2, default=str))
else:
    print(json.dumps({
        "sql": sql,
        "total_rows": len(result),
        "result": result
    }, indent=2, default=str))