# Accounting Bot

A simple Telegram bot that records income and expenses to a Google Spreadsheet.
Entries are separated per month: the bot will create a sheet named `YYYY-MM`
for the current month if it does not already exist.
The worksheet is initialized with columns `timestamp`, `type`, `amount`, and
`description`.

## Setup

1. Create a Google service account and download the credentials JSON file.
2. Share your spreadsheet with the service account email.
3. Set the following environment variables (see `.env.example`):
   - `TELEGRAM_TOKEN`: token from BotFather.
   - `GOOGLE_APPLICATION_CREDENTIALS`: path to the service account JSON file.
   - `SPREADSHEET_KEY`: the key of your spreadsheet (found in the URL).

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

Copy `.env.example` to `.env` and fill in your credentials to run the bot.

Use commands `/income` and `/expense` in Telegram to record data.
