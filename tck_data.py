import pandas as pd
import pymysql
import datetime
import os

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
today = datetime.date.today()
datefrom = datetime.date(today.year, 1, 1)
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

final_df = pd.read_sql(tck_query, conn)

# ==============================
# SAVE TO CSV
# ==============================
final_df.to_csv(output_path, index=False)
print(f"✅ Report saved: {output_path}")
