from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, round, stddev
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("StockVolatilityAnalysis") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Load stock dataset
df = spark.read.csv(
    "stock_data.csv",
    header=True,
    inferSchema=True
)

# Define window for previous price
stock_window = Window \
    .partitionBy("Stock") \
    .orderBy("Timestamp")

# Calculate previous day's price
returns = df.withColumn(
    "Previous_Price",
    lag("Price", 1).over(stock_window)
)

# Calculate daily return percentage
returns = returns.withColumn(
    "Daily_Return",
    ((col("Price") - col("Previous_Price"))
    / col("Previous_Price")) * 100
)

# Calculate volatility using standard deviation
volatility = returns.groupBy("Stock").agg(
    round(stddev("Daily_Return"), 2).alias("Volatility")
)

print("\n--- STOCK VOLATILITY ANALYSIS ---")
volatility.orderBy(
    col("Volatility").desc()
).show()

spark.stop()
