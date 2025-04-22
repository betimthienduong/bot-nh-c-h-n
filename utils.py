import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

SHEET_ID = "1ECtU9jLUHFeAqpH5UggdFjkiEeicq6F_ZHGD9RGsBGc"
SHEET_NAME = "chatgpt"

def get_expiring_accounts():
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    rows = sheet.get_all_values()

    today = datetime.today().date()
    results = []

    for row in rows[1:]:  # Bỏ qua header
        if len(row) < 16:
            continue
        if "Khuyên" not in row[2]:  # Lọc theo tên ở cột C
            continue
        try:
            remaining_days = int(row[11])
        except:
            continue
        if remaining_days in [0, 1]:
            results.append({
                "platform": row[2],         # C
                "account": row[5],          # f
                "date_reg": row[8],         # i
                "Giá bán": row[15],          # G
                "exp_date": row[9],        # K
                "remaining": remaining_days
            })
    return results
