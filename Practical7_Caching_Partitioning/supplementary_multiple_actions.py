from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, count, max, min
import time

spark = SparkSession.builder \
    .appName("MultipleSparkActions") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark.read.csv(
    "ratings.csv",
    header=True,
    inferSchema=True
)

print("\n--- MULTIPLE SPARK ACTIONS PERFORMANCE ---")

actions = [
    ("Count", lambda: df.count()),
    ("Show", lambda: df.show()),
    ("Collect", lambda: df.collect()),
    ("Average Rating", lambda: df.agg(avg("rating")).collect()),
    ("Maximum Rating", lambda: df.agg(max("rating")).collect()),
    ("Minimum Rating", lambda: df.agg(min("rating")).collect())
]

for name, action in actions:
    start = time.time()
    action()
    execution_time = time.time() - start

    print(
        name,
        "execution time:",
        round(execution_time, 4),
        "seconds"
    )

print("\n--- MULTIPLE ACTIONS COMPLETED ---")

spark.stop()
