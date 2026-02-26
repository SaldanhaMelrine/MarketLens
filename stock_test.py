import yfinance as yf
import matplotlib.pyplot as plt

stock = yf.Ticker("AAPL")
data = stock.history(period="1mo")

# Calculate 5-day moving average
data["MA5"] = data["Close"].rolling(window=5).mean()

# Plot
plt.figure()
plt.plot(data["Close"])
plt.plot(data["MA5"])
plt.title("AAPL Price vs 5-Day Moving Average")
plt.show()