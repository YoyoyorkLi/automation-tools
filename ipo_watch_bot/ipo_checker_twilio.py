# Twilio SMS alerts are reliable and fast, but not free
# For free tier twilio, every recipient's number must be verified
# run this script every 5-10 mins during scheduled IPO date
# change up message content and subject everytime to avoid being blocked by your carrier
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestBarRequest
from datetime import datetime, timedelta, timezone
from twilio.rest import Client

# Alpaca API Setup for stock activity
# Set up free personal alpaca API before executing script
API_KEY = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"
client = StockHistoricalDataClient(API_KEY, SECRET_KEY)

# Twilio Setup
TWILIO_ACCOUNT_SID = "YOUR_SID" # Your SID
TWILIO_AUTH_TOKEN = "YOUT_TOKEN"    # Your token
TWILIO_PHONE_NUMBER = "YOUR_TWILIO_NUMBER"  # Your Twilio number

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# SMS Alert
def send_sms_alert(ticker, timestamp, recipients):
    time_str = timestamp.strftime('%Y-%m-%d %H:%M UTC')
    message_body = f"{ticker} is now trading! Last trade: {time_str}. Go get some bread dawg"

    for recipient in recipients:
        try:
            message = twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=recipient
            )
            print(f"[INFO] Sent SMS to {recipient}: SID={message.sid}")
        except Exception as e:
            print(f"[ERROR] Failed to send SMS to {recipient}: {e}")

# Live Trading Check
def is_live(ticker):
    try:
        request = StockLatestBarRequest(symbol_or_symbols=ticker)
        bar = client.get_stock_latest_bar(request)
        bar_data = bar[ticker]

        now = datetime.now(timezone.utc)
        recent_cutoff = now - timedelta(days=3)

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
    watchlist = ["AAPL", "FIG", "STRP", "SI"]

    phone_numbers = [
        "+11234567890",  # Example number
        "+10123456789"   # Example friend/client's number
    ]

    for symbol in watchlist:
        last_trade_time = is_live(symbol)
        if last_trade_time:
            send_sms_alert(symbol, last_trade_time, phone_numbers)