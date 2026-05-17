import base64
import json
import os
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _load_service_account_credentials():
    raw = os.getenv("GOOGLE_SERVICE_ACCOUNT")
    if not raw:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT env var")

    raw = raw.strip()
    try:
        decoded = base64.b64decode(raw).decode("utf-8")
        credentials_json = json.loads(decoded)
    except Exception:
        credentials_json = json.loads(raw)

    return Credentials.from_service_account_info(credentials_json, scopes=SCOPES)


class GoogleSheetsClient:
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.creds = _load_service_account_credentials()
        self.service = build("sheets", "v4", credentials=self.creds)

    def append_row(self, row: list[str]):
        body = {"values": [row]}
        result = (
            self.service.spreadsheets()
            .values()
            .append(
                spreadsheetId=self.spreadsheet_id,
                range="Sheet1!A:E",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        return result

    def ensure_header(self):
        header = [["Tanggal", "Jumlah", "Kategori", "Catatan", "Mata Uang"]]
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range="Sheet1!A1:E1",
            valueInputOption="RAW",
            body={"values": header},
        ).execute()

    @staticmethod
    def build_row(amount: float, category: str, note: str | None, currency: str = "IDR") -> list[str]:
        tanggal = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        return [tanggal, str(amount), category, note or "", currency]
