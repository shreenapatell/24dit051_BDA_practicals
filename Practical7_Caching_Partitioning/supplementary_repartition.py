from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
import time

spark = SparkSession.builder \
    .appName("RepartitionPerformance") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark.read.csv(
    "ratings.csv",
    header=True,
    inferSchema=True
)

print("\n--- REPARTITION PERFORMANCE COMPARISON ---")

for partitions in [2, 4, 8]:
    repartitioned_df = df.repartition(partitions)

    actual_partitions = repartitioned_df.rdd.getNumPartitions()

    start = time.time()

    repartitioned_df.groupBy("movieId") \
        .agg(avg("rating").alias("Average_Rating")) \
        .show()

    execution_time = time.time() - start

    print(
        "Partitions:", actual_partitions,
        "| Execution time:", round(execution_time, 4),
        "seconds"
    )

spark.stop()
