import csv
import time
import random
import os
from datetime import datetime

# Configuration
CSV_FILE = "stock_data.csv"
TICKERS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

# Initial baseline prices to simulate realistic stock market starting points
BASE_PRICES = {
    "AAPL": 175.0,
    "GOOGL": 150.0,
    "MSFT": 400.0,
    "AMZN": 180.0,
    "TSLA": 170.0
}

# Alert Thresholds (Percentage change from the last known price to trigger an alert)
ALERT_THRESHOLD_PCT = 0.5  # 0.5% change

def init_csv():
    """Initializes the CSV file with structured columns if it does not exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Ticker", "Price"])
        print(f"Initialized storage database: {CSV_FILE}")

def get_latest_prices():
    """Reads the CSV file to retrieve the most recent recorded price for each ticker."""
    latest_prices = BASE_PRICES.copy()
    if not os.path.exists(CSV_FILE):
        return latest_prices
        
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            latest_prices[row["Ticker"]] = float(row["Price"])
    return latest_prices

def fetch_fake_api_data(current_prices):
    """Simulates a live stock exchange streaming API by mutating prices via random distributions."""
    simulated_data = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for ticker in TICKERS:
        last_price = current_prices[ticker]
        # Generate a random fluctuation between -1.0% and +1.0%
        change_percent = random.uniform(-1.0, 1.0)
        new_price = round(last_price * (1 + change_percent / 100), 2)
        
        simulated_data.append({
            "timestamp": timestamp,
            "ticker": ticker,
            "price": new_price,
            "change_pct": change_percent
        })
    return simulated_data

def save_to_csv(data_points):
    """Appends time-series stock metrics directly onto the historical CSV layer."""
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        for dp in data_points:
            writer.writerow([dp["timestamp"], dp["ticker"], dp["price"]])

def check_alerts(data_points, previous_prices):
    """Computes pricing drift over intervals and triggers notifications if thresholds are violated."""
    print("\n--- Real-Time Updates & Alerts ---")
    for dp in data_points:
        ticker = dp["ticker"]
        new_price = dp["price"]
        old_price = previous_prices[ticker]
        
        # Calculate percent change from the specific last recorded price ticker
        actual_change_pct = ((new_price - old_price) / old_price) * 100
        
        print(f"[{dp['timestamp']}] {ticker}: ${new_price:<7} ({actual_change_pct:+.2f}%)")
        
        # Check against target absolute percentage constraint 
        if abs(actual_change_pct) >= ALERT_THRESHOLD_PCT:
            direction = "🔺 SPIKE" if actual_change_pct > 0 else "🔻 DROP"
            print(f"🚨 ALERT! {ticker} experienced a sudden {direction}! "
                  f"Price moved from ${old_price:.2f} to ${new_price:.2f} ({actual_change_pct:+.2f}%)")

def display_historical_data(ticker=None):
    """Parses historical metrics stored natively within the local CSV structure."""
    if not os.path.exists(CSV_FILE):
        print("No historical data available yet.")
        return
        
    print(f"\n--- Historical Logs {'for ' + ticker if ticker else ''} ---")
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        count = 0
        for row in reader:
            if ticker and row["Ticker"] != ticker:
                continue
            print(f"{row['Timestamp']} | {row['Ticker']}: ${row['Price']}")
            count += 1
            if count >= 15:
                print("... (Showing first 15 entries)")
                break

def main():
    init_csv()
    print("Starting Live Stock Tracker Loop... Press Ctrl+C to terminate application gracefully.")
    
    try:
        while True:
            # 1. Fetch current baseline states from disk
            current_states = get_latest_prices()
            
            # 2. Query the fake API gateway
            new_ticks = fetch_fake_api_data(current_states)
            
            # 3. Handle threshold validations and real-time outputs
            check_alerts(new_ticks, current_states)
            
            # 4. Commit data transactions to persistence layer
            save_to_csv(new_ticks)
            
            # 5. Delay execution for 3 seconds before next streaming tick
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\nTracker stopped by user.")
        # Print a short snapshot of past ticks upon exit
        display_historical_data()

if __name__ == "__main__":
    main()
