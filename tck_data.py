import pandas as pd
import pymysql
import datetime
import os
from dateutil.relativedelta import relativedelta

# ==============================
# DB CONFIG (Direct MySQL connection)
# ==============================
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASS = "root123!"
DB_NAME = "tck_data"
DB_PORT = 3306

# === Output path ===
output_path = "/home/iccsadmin/Ticket_Data/media/tck_data.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ==============================
# DATE RANGE (from 1st Jan this year to today)
# ==============================
# today = datetime.date.today()
# datefrom = datetime.date(today.year, 1, 1)
# dateto = today

today = datetime.date.today()
start_date = today - relativedelta(months=15)

datefrom = datetime.date(start_date.year, start_date.month, 1)
dateto = today

# ==============================
# SQL QUERY
# ==============================
tck_query = f"""
SELECT 
    users.name as `Ticket User Name`,
    users.ats_id as `Ticket User ATS ID`,
    users.Process as `Process Name`,
    ticketinfos.created_at AS `Ticket Raised Time`,
    ticketinfos.TicketNumber,
    ticketinfos.site_name as Site,
    users.Department_Name as `Ticket Owner Department`,
    time_contoll_lists.Department AS Department,
    ticketinfos.Sub_Dapartment as `Sub Department`,
    ticketinfos.Issue,
    ticketinfos.Sub_Issue as `Sub Issue`,
    ticketinfos.Priority as `Priority`,
    ticketinfos.Remark,
    ticketinfos.Status as `Department Ticket Status`,
    ticketinfos.Issue_status as `Employee Issue Status`,
    ticketinfos.Affected_Counr_users as `Total Users Affected`,
    time_contoll_lists.L1_TAT_Time AS `L1_TAT_Time`,
    
    IF(TIMEDIFF(NOW(), ticketinfos.created_at) < time_contoll_lists.L1_TAT_Time,
        TIMEDIFF(time_contoll_lists.L1_TAT_Time, TIMEDIFF(NOW(), ticketinfos.created_at)),
        '00:00:00') AS `L1 TAT Time`,

    IF(TIMEDIFF(NOW(), ticketinfos.created_at) < ADDTIME(time_contoll_lists.L1_TAT_Time, time_contoll_lists.L2_TAT_Time),
        TIMEDIFF(ADDTIME(time_contoll_lists.L1_TAT_Time, time_contoll_lists.L2_TAT_Time), TIMEDIFF(NOW(), ticketinfos.created_at)),
        '00:00:00') AS `L2 TAT Time`,

    IF(TIMEDIFF(NOW(), ticketinfos.created_at) < ADDTIME(time_contoll_lists.L3_TAT_Time, ADDTIME(time_contoll_lists.L2_TAT_Time, time_contoll_lists.L2_TAT_Time)),
        TIMEDIFF(ADDTIME(time_contoll_lists.L1_TAT_Time, ADDTIME(time_contoll_lists.L2_TAT_Time, time_contoll_lists.L3_TAT_Time)), TIMEDIFF(NOW(), ticketinfos.created_at)),
        '00:00:00') AS `L3 TAT Time`,

    ticketinfos.resolveBy as `Resolved By`,
    users.working_by as `Working By`,
    ticketinfos.ip as `System IP`,
    ticketinfos.close_ats_id as `Close By`,

    IF(ticketinfos.Issue_status = 'Close',
        TIMEDIFF(ticketinfos.ticket_close_datetime, ticketinfos.created_at),
        '00:00:00') AS `Total Resolve Time`,
    
    ticketinfos.ticket_close_datetime as `Ticket Close Datetime`
FROM ticketinfos
JOIN users ON users.id = ticketinfos.userid
JOIN email_user_lists ON email_user_lists.lavel_id = ticketinfos.lavel_id
JOIN time_contoll_lists ON time_contoll_lists.id = ticketinfos.Department
WHERE ticketinfos.created_at BETWEEN '{datefrom}' AND '{dateto}';
"""

# ==============================
# MAIN SCRIPT (Direct MySQL)
# ==============================
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    db=DB_NAME,
    port=DB_PORT
)

# final_df = pd.read_sql(tck_query, conn)

# # ==============================
# # SAVE TO CSV
# # ==============================
# final_df.to_csv(output_path, index=False)
# print(f"✅ Report saved: {output_path}")


final_df = pd.read_sql(tck_query, conn)
conn.close()

# ==============================
# CONVERT MySQL Timedelta → HH:MM:SS
# ==============================
def convert_to_total_hms(x):
    if pd.isna(x):
        return ""
    try:
        td = pd.to_timedelta(x)
        total_seconds = int(td.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except:
        return x

columns_to_clean = [
    "L1_TAT_Time",      # newly added
    "L1 TAT Time",
    "L2 TAT Time",
    "L3 TAT Time",
    "Total Resolve Time"
]

for col in columns_to_clean:
    if col in final_df.columns:
        final_df[col] = final_df[col].apply(convert_to_total_hms)

# ==============================
# SAVE TO CSV
# ==============================
final_df.to_csv(output_path, index=False)
print(f"✅ Report saved: {output_path}")

