from flask import Flask, render_template
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import time

# Load API keys
load_dotenv()

app = Flask(__name__)

# Logging setup
logging.basicConfig(level=logging.INFO)

# Fetch sentiment analysis from CoinGecko
def get_sentiment(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    data = response.json()
    return {
        "up_votes": data.get("sentiment_votes_up_percentage", 0),
        "down_votes": data.get("sentiment_votes_down_percentage", 0)
    }

# Fetch historical price data from CryptoCompare for the last 30 days
def get_cmc_data(symbol):
    url = "https://min-api.cryptocompare.com/data/v2/histoday"
    headers = {"Authorization": f"Apikey {'8b62eb1979993f425969ddffe34870713442856b07bb94f7faab7feba2b86df8'}"}
    
    # Calculate the date 30 days ago from today
    end_date = int(datetime.now().timestamp())  # Current time in Unix timestamp
    start_date = int((datetime.now() - timedelta(days=30)).timestamp())  # 30 days ago in Unix timestamp
    
    params = {
        "fsym": symbol.upper(),  # Cryptocurrency symbol (e.g., BTC, ETH, SOL)
        "tsym": "USD",  # Target currency (USD)
        "limit": 30,  # Number of data points (30 days)
        "toTs": end_date  # End date for the historical data
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        if data["Response"] == "Error":
            logging.error(f"Error fetching data for {symbol}: {data['Message']}")
            return {"labels": [], "prices": [], "volumes": [], "market_caps": []}
        
        return {
            "labels": [datetime.utcfromtimestamp(item["time"]).strftime('%Y-%m-%d') for item in data["Data"]["Data"]],
            "prices": [item["close"] for item in data["Data"]["Data"]],
            "volumes": [item["volumeto"] for item in data["Data"]["Data"]],
            "market_caps": [item["close"] * item["volumeto"] for item in data["Data"]["Data"]]  # Simplified market cap calculation
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data from CryptoCompare: {e}")
        return {"labels": [], "prices": [], "volumes": [], "market_caps": []}


@app.route('/')
def home():
    sentiment_btc = get_sentiment("bitcoin")
    sentiment_eth = get_sentiment("ethereum")
    sentiment_sol = get_sentiment("solana")
    
    btc_data = get_cmc_data("BTC")
    eth_data = get_cmc_data("ETH")
    sol_data = get_cmc_data("SOL")
    
    # Log the fetched data for debugging
    logging.info(f"BTC Data: {btc_data}")
    logging.info(f"ETH Data: {eth_data}")
    logging.info(f"SOL Data: {sol_data}")
    
    return render_template("index.html", 
                           sentiment_btc=sentiment_btc, 
                           sentiment_eth=sentiment_eth, 
                           sentiment_sol=sentiment_sol, 
                           btc_data=btc_data, 
                           eth_data=eth_data, 
                           sol_data=sol_data)

if __name__ == '__main__':
    app.run(debug=True)
