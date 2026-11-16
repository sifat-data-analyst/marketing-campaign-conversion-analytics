import csv
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

BASE = Path(__file__).resolve().parent

LOG_DIR = BASE / "09_Verification_Logs"
LOG_DIR.mkdir(exist_ok=True)

SCHEMAS = {
    "campaigns.csv": {
        "rows": 120,
        "columns": {
            "campaign_id": ("text", 20),
            "campaign_name": ("text", 100),
            "channel": ("text", 30),
            "objective": ("text", 30),
            "start_date": ("date", None),
            "end_date": ("date", None),
            "budget": ("decimal", 18),
        },
        "primary_key": "campaign_id",
    },
    "daily_spend.csv": {
        "rows": 11240,
        "columns": {
            "spend_id": ("text", 20),
            "campaign_id": ("text", 20),
            "spend_date": ("date", None),
            "impressions": ("int", 10),
            "clicks": ("int", 10),
            "spend": ("decimal", 18),
        },
        "primary_key": "spend_id",
    },
    "leads.csv": {
        "rows": 261684,
        "columns": {
            "lead_id": ("text", 20),
            "campaign_id": ("text", 20),
            "created_at": ("date", None),
            "lead_source": ("text", 30),
            "lead_score": ("int", 10),
        },
        "primary_key": "lead_id",
    },
    "conversions.csv": {
        "rows": 39696,
        "columns": {
            "conversion_id": ("text", 20),
            "lead_id": ("text", 20),
            "converted_at": ("date", None),
            "conversion_type": ("text", 30),
            "revenue": ("decimal", 18),
        },
        "primary_key": "conversion_id",
    },
}

report = []
total_pass = 0
total_fail = 0


def log(message):
    report.append(message)
    print(message)


def check(condition, description):
    global total_pass, total_fail

    if condition:
        total_pass += 1
        log("PASS: " + description)
    else:
        total_fail += 1
        log("FAIL: " + description)


log("PROJECT 5 - SQL IMPORT PRECHECK")
log("=" * 60)
log("Audit time: " + datetime.now().isoformat(timespec="seconds"))
log("Original source CSV files will not be modified.")
log("")

for filename, schema in SCHEMAS.items():

    path = BASE / filename

    log("FILE: " + filename)
    log("-" * 50)

    if not path.exists():
        check(False, "File exists: " + filename)
        log("")
        continue

    expected_columns = schema["columns"]
    expected_rows = schema["rows"]
    primary_key = schema["primary_key"]

    actual_rows = 0
    duplicates = 0
    blank_values = 0
    invalid_values = 0
    length_errors = 0
    date_errors = 0
    numeric_errors = 0

    seen_keys = set()

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as file:

            reader = csv.DictReader(file)

            actual_headers = reader.fieldnames

            check(
                actual_headers == list(expected_columns.keys()),
                "Column names and order match SQL schema"
            )

            if actual_headers != list(expected_columns.keys()):
                log("Actual headers: " + str(actual_headers))
                log("")
                continue

            for row in reader:

                actual_rows += 1

                for column, (data_type, limit) in expected_columns.items():

                    value = row.get(column)

                    if value is None or value.strip() == "":
                        blank_values += 1
                        continue

                    value = value.strip()

                    try:

                        if data_type == "text":
                            if len(value) > limit:
                                length_errors += 1

                        elif data_type == "date":
                            datetime.strptime(value, "%Y-%m-%d")

                        elif data_type == "int":
                            number = int(value)

                            if not -2147483648 <= number <= 2147483647:
                                numeric_errors += 1

                        elif data_type == "decimal":
                            number = Decimal(value)

                            if not number.is_finite():
                                raise InvalidOperation

                            if number.as_tuple().exponent < -2:
                                numeric_errors += 1

                            if abs(number) >= Decimal("1e16"):
                                numeric_errors += 1

                    except (ValueError, InvalidOperation):
                        invalid_values += 1

                key = row.get(primary_key, "").strip()

                if key in seen_keys:
                    duplicates += 1
                else:
                    seen_keys.add(key)

        check(
            actual_rows == expected_rows,
            f"Expected row count: {expected_rows:,}; actual: {actual_rows:,}"
        )

        check(blank_values == 0, f"Blank values: {blank_values}")
        check(duplicates == 0, f"Duplicate primary keys: {duplicates}")
        check(length_errors == 0, f"Text length violations: {length_errors}")
        check(date_errors == 0, f"Date validation errors: {date_errors}")
        check(numeric_errors == 0, f"Numeric precision errors: {numeric_errors}")
        check(invalid_values == 0, f"Invalid data values: {invalid_values}")

    except Exception as error:

        check(False, f"File processing error: {type(error).__name__}: {error}")

    log("")

log("=" * 60)
log(f"TOTAL CHECKS PASSED: {total_pass}")
log(f"TOTAL CHECKS FAILED: {total_fail}")

status = "PASS" if total_fail == 0 else "FAIL"

log("OVERALL STATUS: " + status)
log("")

log(
    "NOTE: This is a preliminary source-data precheck. "
    "SQL foreign keys and database constraints require separate validation."
)

report_path = LOG_DIR / "SQL_Import_Precheck_Report.txt"

report_path.write_text(
    "\n".join(report),
    encoding="utf-8"
)

print("")
print("REPORT SAVED:")
print(report_path)
