from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
import time

spark = SparkSession.builder \
    .appName("RatingsScalability") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Original dataset
small_df = spark.read.csv(
    "ratings.csv",
    header=True,
    inferSchema=True
)

# Create a larger dataset by replicating the ratings data
large_df = small_df

for i in range(10):
    large_df = large_df.union(small_df)

print("\n--- DATASET SIZE ---")
print("Original dataset records:", small_df.count())
print("Larger dataset records:", large_df.count())

print("\n--- SMALL DATASET PERFORMANCE ---")

start = time.time()

small_df.groupBy("movieId") \
    .agg(avg("rating").alias("Average_Rating")) \
    .show()

small_time = time.time() - start

print("Small dataset execution time:",
      round(small_time, 4), "seconds")

print("\n--- LARGE DATASET PERFORMANCE ---")

start = time.time()

large_df.groupBy("movieId") \
    .agg(avg("rating").alias("Average_Rating")) \
    .show()

large_time = time.time() - start

print("Large dataset execution time:",
      round(large_time, 4), "seconds")

print("\n--- SCALABILITY COMPARISON ---")
print("Small dataset records:", small_df.count())
print("Large dataset records:", large_df.count())
print("Small dataset time:", round(small_time, 4), "seconds")
print("Large dataset time:", round(large_time, 4), "seconds")

spark.stop()
