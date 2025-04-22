import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = "1ECtU9jLUHFeAqpH5UggdFjkiEeicq6F_ZHGD9RGsBGc"
SHEET_NAME = "chatgpt"

def get_expiring_accounts():
    creds_json = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    rows = sheet.get_all_values()

    today = datetime.today().date()
    results = []

    for row in rows[1:]:  # Bỏ qua header
        if len(row) < 11:
            continue
        if row[2] != "Khuyên":  # Lọc theo tên ở cột C
            continue
        try:
            exp_date = datetime.strptime(row[9], "%Y-%m-%d").date()  # Cột K
        except:
            continue
        remaining_days = (exp_date - today).days
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
