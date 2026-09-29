from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, max, min, col

spark = SparkSession.builder \
    .appName("StockMarketAnalytics") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Load stock dataset
df = spark.read.csv(
    "stock_data.csv",
    header=True,
    inferSchema=True
)

print("\n--- STOCK MARKET DATASET ---")
df.show(50)

print("\n--- DATASET SCHEMA ---")
df.printSchema()

print("\n--- COLUMN DATA TYPES ---")
for column, datatype in df.dtypes:
    print(column, ":", datatype)

# Group records by stock symbol
print("\n--- STOCK-WISE SUMMARY ---")

stock_summary = df.groupBy("Stock").agg(
    avg("Price").alias("Average_Price"),
    max("Price").alias("Maximum_Price"),
    min("Price").alias("Minimum_Price")
)

stock_summary.orderBy("Stock").show()

# Identify best-performing stock based on price increase
print("\n--- BEST-PERFORMING STOCK ---")

first_prices = df.groupBy("Stock").agg(
    min("Timestamp").alias("First_Date")
)

last_prices = df.groupBy("Stock").agg(
    max("Timestamp").alias("Last_Date")
)

df_first = df.alias("d1")
fp = first_prices.alias("fp")

first_data = df_first.join(
    fp,
    (col("d1.Stock") == col("fp.Stock")) &
    (col("d1.Timestamp") == col("fp.First_Date"))
).select(
    col("d1.Stock").alias("Stock"),
    col("d1.Price").alias("Starting_Price")
)

df_last = df.alias("d2")
lp = last_prices.alias("lp")

last_data = df_last.join(
    lp,
    (col("d2.Stock") == col("lp.Stock")) &
    (col("d2.Timestamp") == col("lp.Last_Date"))
).select(
    col("d2.Stock").alias("Stock"),
    col("d2.Price").alias("Ending_Price")
)

performance = first_data.join(
    last_data,
    "Stock"
).withColumn(
    "Price_Change",
    col("Ending_Price") - col("Starting_Price")
).withColumn(
    "Return_Percentage",
    (col("Price_Change") / col("Starting_Price")) * 100
)

performance.orderBy(
    col("Return_Percentage").desc()
).show()

print("\n--- STOCK SUMMARY REPORT ---")
stock_summary.orderBy("Stock").show()

print("\n--- MARKET TREND ANALYSIS ---")
performance.orderBy(
    col("Return_Percentage").desc()
).show()

spark.stop()
