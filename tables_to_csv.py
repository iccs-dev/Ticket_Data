import re
import pandas as pd
from datetime import datetime

# Path to your SQL dump
sql_file = "/home/iccsadmin/ishita/QMS/qms_dump.sql"

# Tables you want to extract
# tables_to_extract = ["roles","cdr_calls", "users", "agent_score_details"]
tables_to_extract = ["cdr_calls"]


# Output directory
output_dir = "/home/iccsadmin/ishita/QMS/media/All/"

with open(sql_file, "r", encoding="utf-8", errors="ignore") as f:
    sql_data = f.read()

for table_name in tables_to_extract:
    print(f"🔍 Processing table: {table_name}")

    # ----------------- Extract column names from CREATE TABLE -----------------
    create_pattern = rf"CREATE TABLE `{table_name}`\s*\((.*?)\)\s*ENGINE="
    create_match = re.search(create_pattern, sql_data, re.DOTALL)

    columns = []
    if create_match:
        cols_def = create_match.group(1)
        columns = re.findall(r"`(.*?)`", cols_def)

    num_cols = len(columns)

    # ----------------- Extract INSERT values -----------------
    insert_pattern = rf"INSERT INTO `{table_name}`.*?VALUES\s*(.*?);"
    matches = re.findall(insert_pattern, sql_data, re.DOTALL)

    rows = []
    for match in matches:
        values = re.findall(r"\((.*?)\)", match, re.DOTALL)
        for val in values:
            row = [col.strip(" '\"") for col in val.split(",")]
            # pad or trim to match number of columns
            if len(row) < num_cols:
                row += [None] * (num_cols - len(row))
            elif len(row) > num_cols:
                row = row[:num_cols]
            rows.append(row)

    # ----------------- Save to CSV -----------------
    if rows:
        csv_file = f"{output_dir}{table_name}.csv"
        df = pd.DataFrame(rows, columns=columns if columns else None)

        # ✅ If 'date' column exists, create a new 'Date' column using extract_or_convert()
        if "date" in df.columns:
            def extract_or_convert(date_val):
                if pd.isna(date_val) or date_val in ["", None]:
                    return None
                try:
                    if isinstance(date_val, str) and " - " in date_val:
                        parsed = pd.to_datetime(date_val.split(" - ")[0], errors="coerce")
                    else:
                        parsed = pd.to_datetime(date_val, errors="coerce")

                    # ✅ Ensure timezone is removed
                    if not pd.isna(parsed):
                        parsed = parsed.tz_localize(None) if hasattr(parsed, "tzinfo") and parsed.tzinfo else parsed
                    return parsed
                except Exception:
                    return None

            df["Date"] = df["date"].apply(extract_or_convert)

            # ----------------- Filter by last year's 1st Jan till today -----------------
            today = datetime.today()
            start_date = datetime(today.year - 1, 1, 1)
            end_date = today

            # ✅ Ensure entire Date column is timezone-naive
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.tz_localize(None)

            df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
            print(f"📅 Filtered data between {start_date.date()} and {end_date.date()}")

            # Convert Date column to dd-mm-yyyy format for final CSV
            df["Date"] = df["Date"].dt.strftime("%d-%m-%Y")


        df.to_csv(csv_file, index=False)
        print(f"✅ Saved {csv_file} with {len(columns)} columns and {len(rows)} rows")
    else:
        print(f"⚠️ No data found for {table_name}")
