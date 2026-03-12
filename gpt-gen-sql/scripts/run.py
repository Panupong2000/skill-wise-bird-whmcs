import sys
import json
import os
import hashlib
import time
import traceback

from ai.sql_generator import generate_sql
from ai.sql_validator import validate_sql
from db.executor import execute_query

# Auto-install openpyxl if needed
try:
    import openpyxl
    import openpyxl.utils
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--target=/tmp/pylib", "openpyxl"])
    sys.path.insert(0, "/tmp/pylib")
    import openpyxl
    import openpyxl.utils

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
EXPORT_THRESHOLD = 100       # rows above this → export to file
EXCEL_PATH = "/tmp/query_result.xlsx"
CSV_PATH = "/tmp/query_result.csv"
CACHE_DIR = "/tmp/sql_cache"
CACHE_TTL = 300              # cache TTL in seconds (5 minutes)


# ---------------------------------------------------------------------------
# Simple file-based query cache
# ---------------------------------------------------------------------------

def _cache_key(sql):
    """Generate a hash key for caching query results."""
    return hashlib.md5(sql.encode()).hexdigest()


def _get_cached(sql):
    """Return cached result if exists and not expired, else None."""
    try:
        key = _cache_key(sql)
        path = os.path.join(CACHE_DIR, f"{key}.json")
        if os.path.exists(path):
            mtime = os.path.getmtime(path)
            if time.time() - mtime < CACHE_TTL:
                with open(path, "r") as f:
                    return json.load(f)
    except Exception:
        pass
    return None


def _set_cache(sql, result):
    """Cache query result to disk."""
    try:
        os.makedirs(CACHE_DIR, exist_ok=True)
        key = _cache_key(sql)
        path = os.path.join(CACHE_DIR, f"{key}.json")
        with open(path, "w") as f:
            json.dump(result, f, default=str)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Export functions
# ---------------------------------------------------------------------------

def _export_excel(result):
    """Export results to Excel file."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Query Result"

    if result:
        headers = list(result[0].keys())
        ws.append(headers)

        for row in result:
            ws.append([str(row.get(h, "")) for h in headers])

        # Auto-width columns
        for col_idx, header in enumerate(headers, 1):
            max_len = len(str(header))
            for r in result[:50]:
                cell_len = len(str(r.get(header, "")))
                if cell_len > max_len:
                    max_len = cell_len
            ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = min(max_len + 2, 50)

    wb.save(EXCEL_PATH)
    return EXCEL_PATH


def _export_csv(result):
    """Export results to CSV file."""
    import csv
    if not result:
        return CSV_PATH

    headers = list(result[0].keys())
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in result:
            writer.writerow({h: str(row.get(h, "")) for h in headers})

    return CSV_PATH


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def main():
    question = " ".join(sys.argv[1:])

    if not question.strip():
        print(json.dumps({
            "error": "No question provided",
            "message": "กรุณาระบุคำถามที่ต้องการค้นหาข้อมูลครับ"
        }, indent=2))
        return

    try:
        # Step 1: Generate SQL
        sql = generate_sql(question)

        # Step 2: Safety validation (may auto-add LIMIT)
        validated_sql = validate_sql(sql)
        if validated_sql:
            sql = validated_sql

        # Step 3: Check cache
        cached = _get_cached(sql)
        if cached is not None:
            result = cached
            from_cache = True
        else:
            # Step 4: Execute query
            result = execute_query(sql)
            _set_cache(sql, result)
            from_cache = False

        # Step 5: Output
        total_rows = len(result)

        if total_rows > EXPORT_THRESHOLD:
            # Export to both Excel and CSV
            excel_path = _export_excel(result)
            csv_path = _export_csv(result)

            print(json.dumps({
                "sql": sql,
                "total_rows": total_rows,
                "export": "file",
                "excel_path": excel_path,
                "csv_path": csv_path,
                "cached": from_cache,
                "message": f"ผลลัพธ์มี {total_rows} รายการ ส่งออกเป็นไฟล์ Excel และ CSV แล้วครับ"
            }, indent=2, default=str))
        else:
            print(json.dumps({
                "sql": sql,
                "total_rows": total_rows,
                "result": result,
                "cached": from_cache
            }, indent=2, default=str))

    except Exception as e:
        error_output = {
            "error": str(e),
            "error_type": type(e).__name__,
            "message": f"เกิดข้อผิดพลาด: {str(e)}"
        }

        # Include SQL if we got that far
        try:
            error_output["sql"] = sql
        except NameError:
            pass

        print(json.dumps(error_output, indent=2, default=str))
        print(traceback.format_exc(), file=sys.stderr)


if __name__ == "__main__":
    main()

# Also run if invoked directly (for sandbox compatibility)
if not hasattr(sys.modules[__name__], '_ran'):
    sys.modules[__name__]._ran = True
    if __name__ != "__main__":
        main()