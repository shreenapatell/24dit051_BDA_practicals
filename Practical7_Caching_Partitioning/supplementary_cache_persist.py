from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
from pyspark import StorageLevel
import time

spark = SparkSession.builder \
    .appName("CacheVsPersist") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark.read.csv(
    "ratings.csv",
    header=True,
    inferSchema=True
)

print("\n--- CACHE() PERFORMANCE ---")

df.cache()

start = time.time()
df.count()
cache_time = time.time() - start

start = time.time()
df.groupBy("movieId").agg(
    avg("rating").alias("Average_Rating")
).show()
cache_action_time = time.time() - start

print("Cache trigger time:", round(cache_time, 4), "seconds")
print("Cached action time:", round(cache_action_time, 4), "seconds")

df.unpersist()

print("\n--- PERSIST(DISK_ONLY) PERFORMANCE ---")

df.persist(StorageLevel.DISK_ONLY)

start = time.time()
df.count()
disk_time = time.time() - start

start = time.time()
df.groupBy("movieId").agg(
    avg("rating").alias("Average_Rating")
).show()
disk_action_time = time.time() - start

print("Disk-only persist trigger time:", round(disk_time, 4), "seconds")
print("Disk-only action time:", round(disk_action_time, 4), "seconds")

print("\n--- CACHE VS PERSIST COMPARISON ---")
print("Cache trigger time:", round(cache_time, 4), "seconds")
print("Cache action time:", round(cache_action_time, 4), "seconds")
print("Disk-only trigger time:", round(disk_time, 4), "seconds")
print("Disk-only action time:", round(disk_action_time, 4), "seconds")

df.unpersist()
spark.stop()
