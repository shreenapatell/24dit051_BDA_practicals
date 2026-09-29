
import pandas as pd
import matplotlib.pyplot as plt

# Load stock dataset
df = pd.read_csv("stock_data.csv")

# Convert Timestamp to date
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Plot stock price trends
for stock in df["Stock"].unique():
    stock_data = df[df["Stock"] == stock]
    plt.plot(
        stock_data["Timestamp"],
        stock_data["Price"],
        marker="o",
        label=stock
    )

plt.title("Stock Price Trends")
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()

plt.savefig("stock_price_trends.png", dpi=300)
plt.show()
