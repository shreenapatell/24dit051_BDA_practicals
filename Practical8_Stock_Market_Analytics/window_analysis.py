from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, round
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("StockWindowAnalysis") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Load stock dataset
df = spark.read.csv(
    "stock_data.csv",
    header=True,
    inferSchema=True
)

# Define window by stock and order by date
stock_window = Window \
    .partitionBy("Stock") \
    .orderBy("Timestamp")

# Calculate previous day's price
daily_returns = df.withColumn(
    "Previous_Price",
    lag("Price", 1).over(stock_window)
)

# Calculate daily return percentage
daily_returns = daily_returns.withColumn(
    "Daily_Return_Percentage",
    round(
        ((col("Price") - col("Previous_Price"))
        / col("Previous_Price")) * 100,
        2
    )
)

print("\n--- DAILY STOCK RETURNS USING WINDOW FUNCTION ---")
daily_returns.orderBy("Stock", "Timestamp").show(50)

spark.stop()
