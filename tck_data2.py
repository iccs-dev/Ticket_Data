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
# DATE RANGE (from 1st Jan last year to today)
# # ==============================
today = datetime.date.today()
datefrom = datetime.date(today.year, 1, 1)   # last year's Jan 01
dateto = today                                   # current date

# SQL QUERIES
# ==============================
# ==============================
# BD INFO EXPORT QUERY
# ==============================
tck_query = f"""
    SELECT
    bd_infos.Company_Name,
    bd_infos.Contact_Name,
    bd_infos.Lead_type,
    bd_infos.Lead_Source,
    bd_infos.Lead_Source_remarks,
    bd_infos.Sales_Stage,
    bd_infos.Prospecting_Stage_Remarks,
    bd_infos.Sub_Sales_Stage,
    bd_infos.Sales_Stage_remarks,
    bd_infos.Forecast_Number_of_Seats,
    bd_infos.Win_Probability,
    bd_infos.Expected_Close_Date,
    bd_infos.Company,
    bd_infos.Next_Steps_remarks,
    bd_infos.Next_Followup_Date,
    bd_infos.Weighted_Forecast,
    bd_infos.Closure_Month,
    bd_infos.Email_ID_of_contact_person,
    bd_infos.Contact_of_contact_person,
    bd_infos.client_Designation,
    bd_infos.Industry_Vertical,
    bd_infos.Number_of_meeting,
    u1.name AS `update By`,
    u2.name AS `Created By`,
    bd_infos.created_at AS `Create Datetime`,
    bd_infos.updated_at AS `Updated Datetime`
FROM
    bd_data.bd_infos
LEFT JOIN bd_data.users AS u1
    ON u1.id = bd_infos.update_userid
LEFT JOIN bd_data.users AS u2
    ON u2.id = bd_infos.userid
WHERE
    bd_infos.created_at BETWEEN '{datefrom} 00:00:00' AND '{dateto} 23:59:59'
ORDER BY
    bd_infos.id DESC;


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
# output_file = "final_report.csv"
final_df.to_csv(output_path, index=False)

print(f"✅ Report saved: {output_path}")
