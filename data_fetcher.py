import yfinance as yf

def fetch_stock_data(ticker, period="3mo"):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period)
    return data