import logging
import os
from datetime import datetime

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, ApplicationBuilder

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from dotenv import load_dotenv
load_dotenv()

# Set up basic logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets setup
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Retrieve environment variables for credentials and spreadsheet
GOOGLE_CREDS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
SPREADSHEET_KEY = os.getenv('SPREADSHEET_KEY')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TELEGRAM_TOKEN:
    raise RuntimeError('TELEGRAM_TOKEN environment variable is required')

# Authenticate with Google Sheets
if GOOGLE_CREDS and SPREADSHEET_KEY:
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDS, SCOPE)
    gclient = gspread.authorize(creds)
    workbook = gclient.open_by_key(SPREADSHEET_KEY)
else:
    workbook = None
    logger.warning('Google Sheets is not configured. Set GOOGLE_APPLICATION_CREDENTIALS and SPREADSHEET_KEY.')


def get_monthly_sheet():
    """Return worksheet for the current month, creating it if needed."""
    if workbook is None:
        return None
    month_title = datetime.utcnow().strftime('%Y-%m')
    try:
        return workbook.worksheet(month_title)
    except gspread.exceptions.WorksheetNotFound:
        ws = workbook.add_worksheet(title=month_title, rows=1000, cols=4)
        ws.append_row(['timestamp', 'type', 'amount', 'description'])
        return ws


def append_record(record_type: str, amount: str, description: str):
    ws = get_monthly_sheet()
    if ws is None:
        logger.error('Google Sheets is not configured')
        return
    timestamp = datetime.utcnow().isoformat()
    row = [timestamp, record_type, amount, description]
    ws.append_row(row)


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Selamat datang di bot akuntansi sederhana! Gunakan /help untuk melihat perintah.')


def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('/income <jumlah> <keterangan> - mencatat pemasukan\n'
                              '/expense <jumlah> <keterangan> - mencatat pengeluaran')


def income(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        update.message.reply_text('Penggunaan: /income <jumlah> <keterangan>')
        return
    amount = context.args[0]
    description = ' '.join(context.args[1:])
    append_record('income', amount, description)
    update.message.reply_text(f'Dicatat pemasukan: {amount} - {description}')


def expense(update: Update, context: CallbackContext) -> None:
    if len(context.args) < 2:
        update.message.reply_text('Penggunaan: /expense <jumlah> <keterangan>')
        return
    amount = context.args[0]
    description = ' '.join(context.args[1:])
    append_record('expense', amount, description)
    update.message.reply_text(f'Dicatat pengeluaran: {amount} - {description}')


def main() -> None:
    print("Starting bot...")
    print(TELEGRAM_TOKEN)

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('income', income))
    app.add_handler(CommandHandler('expense', expense))

    app.run_polling()


if __name__ == '__main__':
    main()
