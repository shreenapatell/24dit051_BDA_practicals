from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
import time

spark = SparkSession.builder \
    .appName("CoalesceVsRepartition") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark.read.csv(
    "ratings.csv",
    header=True,
    inferSchema=True
)

print("\n--- COALESCE VS REPARTITION ---")

# Repartition to 4 partitions
repartitioned_df = df.repartition(4)

start = time.time()

repartitioned_df.groupBy("movieId") \
    .agg(avg("rating").alias("Average_Rating")) \
    .show()

repartition_time = time.time() - start

print("Repartition partitions:",
      repartitioned_df.rdd.getNumPartitions())
print("Repartition execution time:",
      round(repartition_time, 4), "seconds")

# Coalesce to 2 partitions
coalesced_df = repartitioned_df.coalesce(2)

start = time.time()

coalesced_df.groupBy("movieId") \
    .agg(avg("rating").alias("Average_Rating")) \
    .show()

coalesce_time = time.time() - start

print("Coalesce partitions:",
      coalesced_df.rdd.getNumPartitions())
print("Coalesce execution time:",
      round(coalesce_time, 4), "seconds")

print("\n--- PERFORMANCE COMPARISON ---")
print("Repartition time:",
      round(repartition_time, 4), "seconds")
print("Coalesce time:",
      round(coalesce_time, 4), "seconds")

spark.stop()
