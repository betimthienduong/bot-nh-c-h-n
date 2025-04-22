
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = "1ECtU9jLUHFeAqpH5UggdFjkiEeicq6F_ZHGD9RGsBGc"
SHEET_NAME = "Trang tính1"

def get_sheet_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    return sheet.get_all_records()

def get_expiring_accounts():
    data = get_sheet_data()
    today = datetime.today().date()
    results = []

    for row in data:
        if row.get("Tên") != "Khuyên":
            continue
        try:
            exp_date = datetime.strptime(row["Hết hạn"], "%Y-%m-%d").date()
        except:
            continue
        remaining = (exp_date - today).days
        if remaining in [0, 1]:
            results.append({
                "platform": row["Tên"],
                "account": row["Account"],
                "date_reg": row["Date reg"],
                "price": row["Giá bán"],
                "exp_date": exp_date,
                "remaining": remaining
            })
    return results
