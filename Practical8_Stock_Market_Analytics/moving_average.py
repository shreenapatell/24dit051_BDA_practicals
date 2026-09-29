from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, round
from pyspark.sql.window import Window

spark = SparkSession.builder \
    .appName("StockMovingAverage") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Load stock dataset
df = spark.read.csv(
    "stock_data.csv",
    header=True,
    inferSchema=True
)

# Define a 3-day rolling window
moving_window = Window \
    .partitionBy("Stock") \
    .orderBy("Timestamp") \
    .rowsBetween(-2, 0)

# Calculate 3-day moving average
moving_average = df.withColumn(
    "Three_Day_Moving_Average",
    round(avg("Price").over(moving_window), 2)
)

print("\n--- 3-DAY MOVING AVERAGE ---")
moving_average.orderBy("Stock", "Timestamp").show(50)

spark.stop()
