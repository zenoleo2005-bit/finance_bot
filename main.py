import os
import re
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests

load_dotenv()

from sheets import GoogleSheetsClient

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

if not TELEGRAM_TOKEN:
    raise RuntimeError("Missing TELEGRAM_BOT_TOKEN environment variable")
if not SPREADSHEET_ID:
    raise RuntimeError("Missing SPREADSHEET_ID environment variable")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

sheets_client = GoogleSheetsClient(SPREADSHEET_ID)

COMMAND_RE = re.compile(r"^/add\s+(?P<amount>[0-9]+(?:\.[0-9]+)?)\s+(?P<category>\S+)(?:\s+(?P<note>.*))?$", re.IGNORECASE)


def send_telegram_message(chat_id: int, text: str):
    requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )


def parse_add_command(text: str) -> tuple[float, str, Optional[str]]:
    match = COMMAND_RE.match(text.strip())
    if not match:
        raise ValueError("Format salah. Gunakan: /add <jumlah> <kategori> [catatan]")
    amount = float(match.group("amount"))
    category = match.group("category")
    note = match.group("note")
    return amount, category, note


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[dict]


@app.on_event("startup")
def startup_event():
    sheets_client.ensure_header()


@app.post("/webhook")
async def telegram_webhook(update: TelegramUpdate, request: Request):
    if not update.message:
        return {"ok": True}

    message = update.message
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    text = message.get("text", "")

    if not chat_id or not text:
        return {"ok": True}

    if text.strip().lower().startswith("/add"):
        try:
            amount, category, note = parse_add_command(text)
            row = sheets_client.build_row(amount, category, note)
            sheets_client.append_row(row)
            send_telegram_message(chat_id, f"✅ Catatan disimpan: {amount} {category} {note or ''}".strip())
        except ValueError as err:
            send_telegram_message(chat_id, str(err))
        except Exception:
            send_telegram_message(chat_id, "⚠️ Gagal menyimpan catatan. Pastikan sheet dan credentials sudah benar.")
    else:
        send_telegram_message(chat_id, "Gunakan perintah /add <jumlah> <kategori> [catatan]")

    return {"ok": True}
