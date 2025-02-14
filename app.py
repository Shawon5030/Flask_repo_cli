from flask import Flask, render_template
import requests
from dotenv import load_dotenv
import logging
import os

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

# Fetch historical price data from CoinGecko
def get_market_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": 30, "interval": "daily"}
    response = requests.get(url, params=params)
    data = response.json()
    
    if "prices" in data:
        labels = [price[0] for price in data["prices"]]
        prices = [price[1] for price in data["prices"]]
        return {"labels": labels, "data": prices}
    return {"labels": [], "data": []}

@app.route('/')
def home():
    sentiment_btc = get_sentiment("bitcoin")
    sentiment_eth = get_sentiment("ethereum")
    sentiment_sol = get_sentiment("solana")
    
    btc_data = get_market_data("bitcoin")
    eth_data = get_market_data("ethereum")
    sol_data = get_market_data("solana")
    
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
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)