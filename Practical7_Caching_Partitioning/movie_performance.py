from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
import time


# Create Spark Session
spark = SparkSession.builder \
    .appName("MovieFlixPerformanceOptimization") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


# Load ratings dataset
df = spark.read.csv(
    "ratings.csv",
    header=True,
    inferSchema=True
)


# Display dataset
print("\n--- Movie Ratings Dataset ---")
df.show()


# Display schema
print("\n--- Dataset Schema ---")
df.printSchema()


# Display data types
print("\n--- Column Data Types ---")
for column, datatype in df.dtypes:
    print(column, ":", datatype)


# Check initial number of partitions
initial_partitions = df.rdd.getNumPartitions()

print("\n--- Initial Partition Count ---")
print("Number of partitions:", initial_partitions)


# Calculate average movie rating BEFORE caching
print("\n--- Average Rating Before Caching ---")

start_time = time.time()

average_before = df.groupBy("movieId") \
    .agg(avg("rating").alias("Average_Rating"))

average_before.show()

# Trigger the computation
average_before.collect()

before_time = time.time() - start_time

print("Execution time before caching:",
      round(before_time, 4), "seconds")


# Apply cache
df.cache()


# Trigger caching using count()
print("\n--- Triggering Cache ---")

cache_start = time.time()

df.count()

cache_time = time.time() - cache_start

print("Cache trigger count:", df.count())
print("Caching time:",
      round(cache_time, 4), "seconds")


# Calculate average rating AFTER caching
print("\n--- Average Rating After Caching ---")

start_time = time.time()

average_after = df.groupBy("movieId") \
    .agg(avg("rating").alias("Average_Rating"))

average_after.show()

# Trigger computation
average_after.collect()

after_time = time.time() - start_time

print("Execution time after caching:",
      round(after_time, 4), "seconds")


# Repartition dataset into 4 partitions
print("\n--- Repartitioning Dataset ---")

repartitioned_df = df.repartition(4)

updated_partitions = repartitioned_df.rdd.getNumPartitions()

print("Updated number of partitions:",
      updated_partitions)


# Measure execution after repartitioning
print("\n--- Performance After Repartitioning ---")

start_time = time.time()

repartitioned_average = repartitioned_df.groupBy("movieId") \
    .agg(avg("rating").alias("Average_Rating"))

repartitioned_average.show()

repartitioned_average.collect()

repartitioned_time = time.time() - start_time

print("Execution time after repartitioning:",
      round(repartitioned_time, 4), "seconds")


# Performance comparison
print("\n--- Performance Comparison ---")

print("Before caching:",
      round(before_time, 4), "seconds")

print("After caching:",
      round(after_time, 4), "seconds")

print("After repartitioning:",
      round(repartitioned_time, 4), "seconds")

print("Initial partitions:",
      initial_partitions)

print("Partitions after repartitioning:",
      updated_partitions)


# Stop Spark
spark.stop()
