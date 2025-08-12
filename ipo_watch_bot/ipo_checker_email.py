# Automated Gmail to SMS is free but could be laggy and unreliable
# Only run this script 1-2 times per day and change up message content and subject everytime
# to avoid being blocked by your carrier
# run this script every 5-10 mins during scheduled IPO date
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestBarRequest
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText

# Alpaca API Setup for stock activity
# Set up free personal alpaca API before executing script
API_KEY = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"
client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# SMS Alert Setup from Gmail
# Set up two-factor authentication and app password
def send_sms_alert(ticker, last_trade_time, recipients):
    sender_email = "YOUR_EMAIL" # Your email
    app_password = "YOUR_APP_PASSWORD"  # Gmail app password

    trade_time_str = last_trade_time.strftime('%Y-%m-%d %H:%M UTC')
    send_time_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    message = (f"{ticker} is now trading!\n"
               f"Last trade: {trade_time_str}\n"
               f"Alert sent: {send_time_str}\n"
               f"Go get that bread dawg.")

    for recipient in recipients:
        msg = MIMEText(message)
        msg["From"] = sender_email
        msg["To"] = recipient
        msg["Subject"] = "Stock IPO Alert"  # Proper subject to avoid spam filtering

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient, msg.as_string())
                print(f"[INFO] Sent SMS alert for {ticker} to {recipient}")
        except Exception as e:
            print(f"[ERROR] Failed to send SMS for {ticker} to {recipient}: {e}")

# Live Trading Check
def is_live(ticker):
    try:
        request = StockLatestBarRequest(symbol_or_symbols=ticker)
        bar = client.get_stock_latest_bar(request)
        bar_data = bar[ticker]

        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(days=3) # If no activity in 3 days, classify as inactive

        if bar_data.timestamp > recent_cutoff and bar_data.volume > 0:
            print(f"{ticker} is live. Last trade: {bar_data.timestamp}")
            return bar_data.timestamp
        else:
            print(f"{ticker} is not live since {bar_data.timestamp}")
            return None
    except Exception as e:
        print(f"Could not fetch data for {ticker}: {e}")
        return None

# Main
if __name__ == "__main__":
    watchlist = ["FIG"] # Figma IPO
    # Look up appopriate carrier email address for email to SMS alert
    # For example, @vtext.com for Verizon
    phone_numbers = [
        "1234567890@vtext.com"    # Example Verizon number
    ]

    # Execute
    for symbol in watchlist:
        last_trade_time = is_live(symbol)
        if last_trade_time:
            send_sms_alert(symbol, last_trade_time, phone_numbers)
