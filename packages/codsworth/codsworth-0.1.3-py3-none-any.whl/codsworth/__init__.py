import os
import json
import random

import nltk
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import spacy
import requests
import difflib
import pandas as pd
from prophet import Prophet
from datetime import datetime 
import plotly.graph_objs as go
import re

# Define these at the top, after imports
STOCK_KEYWORDS = [
    "stock", "stocks", "aapl", "msft", "goog", "tsla", "amzn", "meta", "nvda", "intc", "ibm", "orcl",
    "brk.a", "brk.b", "v", "jpm", "wmt", "pg", "dis", "nflx", "baba", "ba", "ge", "gm", "f"
]
CRYPTO_KEYWORDS = [
    "crypto", "bitcoin", "ethereum", "cardano", "dogecoin", "litecoin", "solana", "bnb", "ripple", "xrp",
    "polkadot", "tron", "shiba", "matic", "ada", "btc", "ltc", "bnb", "doge", "cro", "crypto-com-chain"
]
PREDICTION_KEYWORDS = ["predict", "prediction", "forecast"]

SUPPORTED_COINS = [
    "bitcoin", "ethereum", "solana", "dogecoin", "litecoin", "cardano", "binancecoin", "ripple", "polkadot",
    "tron", "shiba-inu", "matic-network", "usd-coin", "tether", "pepe", "arbitrum", "sui", "bifi", "grail",
    "crypto-com-chain", "cro" 
]

class ChatbotModel(nn.Module):
   
    def __init__(self, input_size, output_size):
        super(ChatbotModel, self).__init__()

        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.5)
      
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
         
        return x

class ChatbotAssistant:

    def __init__(self, intents_path, function_mappings = None):
        self.model = None
        self.intents_path = intents_path
        self.nlp = spacy.load("en_core_web_md")
        self.pattern_response_map = {}
    
        with open(intents_path, 'r') as f:
            intents_data = json.load(f)
        self.summarize_patterns = []
        for intent in intents_data['intents']:
            if intent.get("tag") == "summarize":
                self.summarize_patterns = [p.lower() for p in intent.get("patterns", [])]

        self.documents = []
        self.vocabulary = []
        self.intents = []
        self.intents_responses = {}
        self.context = {}

        self.function_mappings = function_mappings

        self.X = None
        self.y = None

    def extract_entities(self, text):
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents]
    
    @staticmethod
    def tokenize_and_lemmatize(text):
        lemmatizer = nltk.WordNetLemmatizer()
        
        words = nltk.word_tokenize(text)
        words = [lemmatizer.lemmatize(word.lower()) for word in words]

        return words

    def pattern_vector(self, text):
        doc = self.nlp(text)
        vectors = [token.vector for token in doc if token.has_vector]
        if vectors:
            return np.mean(vectors, axis=0)
        else:
            return np.zeros(self.nlp.vocab.vectors_length)
    
    def parse_intents(self):
        lemmatizer = nltk.WordNetLemmatizer()

        if os.path.exists(self.intents_path):
            with open(self.intents_path, 'r') as f:
                intents_data = json.load(f)
                
            for intent in intents_data['intents']:
                if intent['tag'] not in self.intents:
                    self.intents.append(intent['tag'])
                    self.intents_responses[intent['tag']] = intent['responses']       

                for i, pattern in enumerate(intent['patterns']):
                    pattern_words = self.tokenize_and_lemmatize(pattern)
                    self.vocabulary.extend(pattern_words)
                    self.documents.append((pattern_words, intent['tag']))
                    if intent['responses']:
                        self.pattern_response_map[pattern.lower()] = intent['responses'][min(i, len(intent['responses'])-1)]
                self.vocabulary = sorted(set(self.vocabulary))

                for pattern in intent['patterns']:
                    pattern_words = self.tokenize_and_lemmatize(pattern)
                    self.vocabulary.extend(pattern_words)
                    self.documents.append((pattern_words, intent['tag']))
                    
            self.vocabulary = sorted(set(self.vocabulary))
   
    def prepare_data(self):
        vectors = []
        indices = []
        for document in self.documents:
            pattern_text = " ".join(document[0])
            vec = self.pattern_vector(pattern_text)
            vectors.append(vec)
            intent_index = self.intents.index(document[1])
            indices.append(intent_index)
        self.X = np.array(vectors)
        self.y = np.array(indices)
 
    def train_model(self, batch_size, lr, epochs):
        X_tensor = torch.tensor(self.X, dtype=torch.float32)
        y_tensor = torch.tensor(self.y, dtype=torch.long)

        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        self.model = ChatbotModel(self.X.shape[1], len(self.intents))

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)

        for epoch in range(epochs):
            running_loss = 0.0

            for batch_X, batch_y in loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                running_loss += loss.item()

            print(f"Epoch {epoch+1}: Loss: {running_loss / len(loader):.4f}")
    
    def save_model(self, model_path, dimensions_path):
        torch.save(self.model.state_dict(), model_path)
            
        with open(dimensions_path, 'w') as f:
            json.dump({ 'input_size': self.X.shape[1], 'output_size': len(self.intents) }, f)

    def load_model(self, model_path, dimensions_path):
        with open(dimensions_path, 'r') as f:
            dimensions = json.load(f)

            self.model = ChatbotModel(dimensions['input_size'], dimensions['output_size'])
            self.model.load_state_dict(torch.load(model_path))

    import re 

    def extract_days(self, user_input):
        user_input = user_input.lower()
        if re.search(r'24 ?hours?', user_input) or re.search(r'1 ?day', user_input):
            return 1
        match = re.search(r'for (\d+) days?', user_input)
        if match:
            return max(1, min(365, int(match.group(1))))
        match = re.search(r'for (\d+) weeks?', user_input)
        if match:
            return max(1, min(365, int(match.group(1)) * 7))
        match = re.search(r'for (\d+) months?', user_input)
        if match:
            return max(1, min(365, int(match.group(1)) * 30))
        if re.search(r'for (a|1) year', user_input):
            return 365
        return 7

    def process_message(self, input_message):
        user_input = input_message.lower()
        
        prediction_keywords = PREDICTION_KEYWORDS
        crypto_keywords = CRYPTO_KEYWORDS
        stock_keywords = STOCK_KEYWORDS

        for pattern in self.summarize_patterns:
            if pattern in user_input or difflib.SequenceMatcher(None, pattern, user_input).ratio() > 0.85:
                headlines_text = get_latest_headlines()
                if headlines_text:
                    return self.function_mappings["summarize"](headlines_text)
                else:
                    return "Sorry, I could not retreive the news to summarize"

        if "weather" in user_input:
            if self.function_mappings and "weather" in self.function_mappings:
                return self.function_mappings["weather"](entities=self.extract_entities(input_message))

        if "news" in user_input:
            if self.function_mappings and "news" in self.function_mappings:
                return self.function_mappings["news"](entities=self.extract_entities(input_message))
    
        vec = self.pattern_vector(input_message)
        vec = np.array(vec, dtype=np.float32)
        vec_tensor = torch.from_numpy(vec).unsqueeze(0)

        self.model.eval()
        with torch.no_grad():
            predictions = self.model(vec_tensor)
            predicted_class_index = torch.argmax(predictions, dim=1).item()
            predicted_intent = self.intents[predicted_class_index]
            entities = self.extract_entities(input_message)

            self.context['last_intent'] = predicted_intent
            self.context['last_entities'] = entities

            # --- SUMMARIZE INTENT HANDLING ---
            if predicted_intent == "summarize" and self.function_mappings and "summarize" in self.function_mappings:
                headlines_text = get_latest_headlines()
                if headlines_text:
                    return self.function_mappings["summarize"](headlines_text)
                else:
                    return "Sorry, I couldn't fetch news to summarize."
        
        # --- Stock price query 
        if any(word in user_input for word in stock_keywords) and ("price" in user_input or "quote" in user_input):
            if self.function_mappings and "stocks" in self.function_mappings:
                return self.function_mappings["stocks"](user_input=user_input)

            # --- Stock/Crypto Predection Blocks
        if any(pred_word in user_input for pred_word in prediction_keywords) and any(word in user_input for word in stock_keywords):
            if self.function_mappings and "stock_predict" in self.function_mappings:
                days_ahead = self.extract_days(user_input)
                for word in user_input.upper().split():
                    if word in [k.upper() for k in stock_keywords]:
                        return self.function_mappings["stock_predict"](symbol=word, days_ahead=days_ahead)
                return self.function_mappings["stock_predict"](days_ahead=days_ahead)

        if any(pred_word in user_input for pred_word in prediction_keywords) and any(word in user_input for word in crypto_keywords):
            if self.function_mappings and "crypto_predict" in self.function_mappings:
                days_ahead = self.extract_days(user_input)
                for word in user_input.split():
                    if word in crypto_keywords:
                        return self.function_mappings["crypto_predict"](symbol=word, days_ahead=days_ahead)
                return self.function_mappings["crypto_predict"](days_ahead=days_ahead)

            # --- Other function mappings --
            if self.function_mappings and predicted_intent in self.function_mappings:
                # Special handling for stock_predict and crypto_predict
                if predicted_intent == "stock_predict":
                    # Try to extract symbol and days from user_input
                    days_ahead = self.extract_days(user_input)
                    symbol = None
                    for word in user_input.upper().split():
                        if word in [k.upper() for k in STOCK_KEYWORDS]:
                            symbol = word
                            break
                    if symbol:
                         return self.function_mappings["stock_predict"](symbol=symbol, days_ahead=days_ahead)
                    else:
                        return self.function_mappings["stock_predict"](days_ahead=days_ahead)
        elif predicted_intent == "crypto_predict":
            days_ahead = self.extract_days(user_input)
            symbol = None
            for word in user_input.split():
                if word in CRYPTO_KEYWORDS:
                    symbol = word
                    break
            if symbol:
                return self.function_mappings["crypto_predict"](symbol=symbol, days_ahead=days_ahead)
            else:
                return self.function_mappings["crypto_predict"](days_ahead=days_ahead)
        else:
            return self.function_mappings[predicted_intent](entities=entities)

            # --- Last resort ---

        if predicted_intent in self.intents_responses and self.intents_responses[predicted_intent]:
            return random.choice(self.intents_responses[predicted_intent])

        closest = difflib.get_close_matches(user_input, self.pattern_response_map.keys(), n=1, cutoff=0.85)
        if closest:
            return self.pattern_response_map[closest[0]]  
        if user_input in self.pattern_response_map:
            return self.pattern_response_map[user_input]
               
from textblob import TextBlob
def get_news_sentiment(entities=None):
    api_key = "b6b16e439c404ec89c96cdb0c8b667f6"
    url = f"https://newsapi.org/v2/top-headlines?sources=cnn,bbc-news,fox-news,reuters,the-new-york-times&apiKey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") == "ok":
            articles = data.get("articles", [])[:5]
            headlines = [a['title'] for a in articles]
            sentiments = [TextBlob(h).sentiment.polarity for h in headlines]
            avg_sentiment = sum(sentiments) / len(sentiments)
            mood = "positive" if avg_sentiment > 0 else "negative" if avg_sentiment < 0 else "neutral"
            return f"Overall news sentiment is {mood} (score: {avg_sentiment:.2f}).\n" + "\n".join(f"- {h}" for h in headlines)
        else:
            return "Sorry, I could not retrieve the news."
    except Exception as e:
        return f"Error connecting to news service: {e}"
         
def get_latest_headlines():
    api_key = "b6b16e439c404ec89c96cdb0c8b667f6"
    url = f"https://newsapi.org/v2/top-headlines?sources=cnn,bbc-news,fox-news,reuters,the-new-york-times&apiKey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        if data.get("status") == "ok":
            articles = data.get("articles", [])[:5]
            return " ".join(a['title'] for a in articles)
        else:
            return ""
    except Exception:
        return ""
    
from transformers import pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
def summarize_news_article(article_text):
    summary = summarizer(article_text, max_length=60, do_sample=False)
    return summary[0]['summary_text']

def get_crypto(entities=None, user_input=None):
    symbol = "bitcoin"
    # List of supported coins (CoinGecko IDs)
    ticker_map = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "doge": "dogecoin",
        "ltc": "litecoin",
        "cro": "crypto-com-chain",
        "cronos": "crypto-com-chain",
        "ada": "cardano",
        "bnb": "binancecoin",
        "xrp": "ripple",
        "dot": "polkadot",
        "trx": "tron",
        "shib": "shiba-inu",
        "matic": "matic-network",
        "usdc": "usd-coin",
        "usdt": "tether",
        "pepe": "pepe",
        "arb": "arbitrum",
        "sui": "sui",
        "bifi": "bifi",
        "grail": "grail"
    }
  
    # Try to extract from entities
    if entities:
        for ent, label in entities:
            ent_lower = ent.lower()
            if ent_lower in SUPPORTED_COINS:
                symbol = ent_lower
                break
            if ent_lower in ticker_map:
                symbol = ticker_map[ent_lower]
                break
    # Fallback: check user_input for coin names/tickers
    if user_input:
        for word in user_input.lower().split():
            if word in SUPPORTED_COINS:
                symbol = word
                break
            if word in ticker_map:
                symbol = ticker_map[word]
                break

    if symbol not in SUPPORTED_COINS:
        return f"{symbol} is not supported."

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd&include_24hr_change=true"
    try:
        response = requests.get(url)
        data = response.json()
        price = data.get(symbol, {}).get("usd")
        change = data.get(symbol, {}).get("usd_24h_change")
        if price is not None and change is not None:
            change_str = f"{change:+.2f}%"
            return f"The current price of {symbol.replace('-', ' ').capitalize()} is ${price:.2f} (24h change: {change_str})"
        elif price is not None:
            return f"The current price of {symbol.replace('-', ' ').capitalize()} is ${price:.2f}" 
        else:
            return f"Sorry, I could not retrieve the price for {symbol}"
    except Exception as e:
        return f"Error connecting to crypto service: {e}"

def predict_crypto(symbol, days_ahead=7):
    if symbol not in SUPPORTED_COINS:
        return f"{symbol} is not supported."

    ticker_map = {
        "btc": "bitcoin",
        "eth": "ethereum",
        "sol": "solana",
        "doge": "dogecoin",
        "ltc": "litecoin",
        "cro": "crypto-com-chain",
        "cronos": "crypto-com-chain",
        "ada": "cardano",
        "bnb": "binancecoin",
        "xrp": "ripple",
        "dot": "polkadot",
        "trx": "tron",
        "shib": "shiba-inu",
        "matic": "matic-network",
        "usdc": "usd-coin",
        "usdt": "tether",
        "pepe": "pepe",
        "arb": "arbitrum",
        "sui": "sui",
        "bifi": "bifi",
        "grail": "grail"
    }

    if symbol.lower() in ticker_map:
        symbol = ticker_map[symbol.lower()]

    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart?vs_currency=usd&days=365"
    try:
        response = requests.get(url)
        data = response.json()
        #print(f"DEBUG: API response for {symbol}:", data)
        prices = data.get("prices", [])
        if not prices or len(prices) < 10:
            return f"Not enough data to make a determination for prediction for {symbol}."
        market_caps = data.get("market_caps", [])
        volumes = data.get("total_volumes", [])
        

        df = pd.DataFrame(prices, columns = ["ds", "y"])
        df["ds"] = pd.to_datetime(df["ds"], unit="ms")
        df["y"] = df["y"].astype(float)
        df["y"] = df["y"].rolling(window=3, min_periods=1).mean()

        df["market_cap"] = [mc[1] for mc in market_caps]
        df["volume"] = [v[1] for v in volumes]
        df["rolling_mean_7"] = df["y"].rolling(window=7, min_periods=1).mean()
        df["rolling_mean_14"] = df["y"].rolling(window =14, min_periods=1).mean()
        df['symbol'] = symbol.lower()
        cols = ['symbol', 'ds', 'y', 'market_cap', 'volume', 'rolling_mean_7', 'rolling_mean_14']
        df = df[cols]
        import os
        print("Appending to CSV. Symbol:", symbol.lower(), "Rows:", len(df))
        print(df.head())
        df.to_csv("cryptodata.csv", mode='a', header=not os.path.exists("cryptodata.csv"), index=False)

        df_all = pd.read_csv("cryptodata.csv")
        symbol_df = df_all[df_all['symbol'] == symbol.lower()]

        model = Prophet(daily_seasonality=True)
        model.add_regressor('market_cap')
        model.add_regressor('volume')
        model.add_regressor('rolling_mean_7')
        model.add_regressor('rolling_mean_14')
        model.fit(symbol_df)

        future = model.make_future_dataframe(periods=days_ahead)
        future["market_cap"] = symbol_df["market_cap"].iloc[-1]
        future["volume"] = symbol_df["volume"].iloc[-1]
        future['rolling_mean_7'] = symbol_df['rolling_mean_7'].iloc[-1]
        future['rolling_mean_14'] = symbol_df['rolling_mean_14'].iloc[-1]
        forecast = model.predict(future)
        
        predicted_price = forecast.iloc[-1]["yhat"]
        lower = forecast.iloc[-1]["yhat_lower"]
        upper = forecast.iloc[-1]["yhat_upper"]
        date_predicted = forecast.iloc[-1]["ds"].strftime("%Y-%m-%d")
        return (f"Predicted price of {symbol.capitalize()} on {date_predicted}: "
                f"${predicted_price:,.2f} (range: ${lower:,.2f} - ${upper:,.2f})")
    except Exception as e:
        return f"Error determining prediction for {symbol}: {e}"

def get_stocks(entities=None, user_input=None):
    """
    Fetches the latest stock price and 24h change for a given symbol using Alpha Vantage.
    """
    api_key = "VV6FUN6DRTNT3IG6"  
    symbol = "AAPL"  

    if entities:
        for ent, label in entities:
            if label == "ORG" or label == "PRODUCT":
                symbol = ent.upper()
                break
    if user_input:
        for word in user_input.upper().split():
            if word.isalpha() and len(word) <= 5:
                symbol = word
                break

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        quote = data.get("Global Quote", {})
        price = quote.get("05. price")
        change = quote.get("10. change percent")
        if price and change:
            return f"The current price of {symbol} is ${float(price):,.2f} (24h change: {change})"
        elif price:
            return f"The current price of {symbol} is ${float(price):,.2f}"
        else:
            return f"Sorry, I could not retrieve the price for {symbol}."
    except Exception as e:
        return f"Error connecting to stock service: {e}"

def predict_stock(symbol="AAPL", days_ahead=7):
    """
    Fetches historical stock data and predicts future price using Prophet.
    """
    api_key = "VV6FUN6DRTNT3IG6"
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=compact&apikey={api_key}"
    try:
        response = requests.get(url)
        data = response.json()
        ts = data.get('Time Series (Daily)', {})
        if not ts:
            print("Alpha Vantage response:", data)
            return f"Could not fetch historical data for {symbol}."
        df = pd.DataFrame.from_dict(ts, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.rename(columns={
            '4. close': 'y',
            '5. volume': 'volume'
        })
        df['y'] = df['y'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['rolling_mean_7'] = df['y'].rolling(window=7, min_periods=1).mean()
        df['rolling_mean_14'] = df['y'].rolling(window=14, min_periods=1).mean()
        df = df.reset_index().rename(columns={'index': 'ds'})
        df['symbol'] = symbol

# Ensure all required columns exist and are in the correct order
        required_cols = [
            'symbol','ds', '1. open', '2. high', '3. low', 'y', 'volume',
            'rolling_mean_7', 'rolling_mean_14'
       ]
        for col in required_cols:
            if col not in df.columns:
                df[col] = np.nan
        df = df[required_cols]  

        df.to_csv("stockdata.csv", mode='a', header=not os.path.exists("stockdata.csv"), index=False)
        
        df = pd.read_csv("stockdata.csv")
        symbol = symbol.upper()
        symbol_df = df[df['symbol'] == symbol]

        if symbol_df.empty:
            return f"No data found for {symbol}"

        model = Prophet(daily_seasonality=True)
        model.add_regressor('volume')
        model.add_regressor('rolling_mean_7')
        model.add_regressor('rolling_mean_14')
        model.fit(symbol_df)

        future = model.make_future_dataframe(periods=days_ahead)
        future['volume'] = symbol_df['volume'].iloc[-1]
        future['rolling_mean_7'] = symbol_df['rolling_mean_7'].iloc[-1]
        future['rolling_mean_14'] = symbol_df['rolling_mean_14'].iloc[-1]
        forecast = model.predict(future)

        predicted_price = forecast.iloc[-1]["yhat"]
        lower = forecast.iloc[-1]["yhat_lower"]
        upper = forecast.iloc[-1]["yhat_upper"]
        date_predicted = forecast.iloc[-1]["ds"].strftime("%Y-%m-%d")
        return (f"Predicted price of {symbol.upper()} on {date_predicted}: "
                f"${predicted_price:,.2f} (range: ${lower:,.2f} - ${upper:,.2f})")
    except Exception as e:
        return f"Error determining prediction for {symbol}: {e}"

def get_weather(entities=None):
    api_key = "0279ad62b5aeb67b15abbb9a977f6a54"  
    location = None
    if entities:
        for ent, label in entities:
            if label == "GPE":
                location = ent
                break
    if not location:
        return "Please specify a location for the weather."
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            return f"The weather in {location} is {desc} with a temperature of {temp}°C"
        else:
            return f"Sorry, I could not retrieve the weather for {location}."
    except Exception as e:
        return f"Error connecting to weather service: {e}"


def main():
    import sys
    if "--train" in sys.argv:
        # TRAINING MODE: Run this ONCE to create the files.
        assistant = ChatbotAssistant(
            'intents.json',
            function_mappings = {
                'stocks': get_stocks,
                'weather': get_weather,
                'crypto': get_crypto,
                'news' : get_news_sentiment,
                'summarize': summarize_news_article,
                'crypto_predict': predict_crypto
            }
        )
        assistant.parse_intents()
        assistant.prepare_data()
        assistant.train_model(batch_size=8, lr=0.001, epochs=100)
        assistant.save_model('chatbot_model.pth', 'dimensions.json')
        print("Model trained and saved!")
    else:
        # CHATBOT MODE: Normal usage
        assistant = ChatbotAssistant(
            'intents.json',
            function_mappings = {
                'stocks': get_stocks,
                'weather': get_weather,
                'crypto': get_crypto,
                'news':  get_news_sentiment,
                'summarize': summarize_news_article,
                'crypto_predict': predict_crypto,
                'stock_predict': predict_stock
            }
        )
        assistant.parse_intents()
        assistant.load_model('chatbot_model.pth', 'dimensions.json')

        while True:
            message = input('Enter your message:')
            if message == '/quit':
                break
            print(assistant.process_message(message))
