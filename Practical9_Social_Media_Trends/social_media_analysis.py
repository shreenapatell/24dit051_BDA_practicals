from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc

spark = SparkSession.builder \
    .appName("SocialMediaTrendDetection") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Step 1: Load dataset
df = spark.read.csv(
    "social_media_data.csv",
    header=True,
    inferSchema=True
)

print("\n--- SOCIAL MEDIA HASHTAG DATA ---")
df.show(20, truncate=False)

# Step 2: Validate dataset structure
print("\n--- DATASET SCHEMA ---")
df.printSchema()

print("\n--- DATASET INFORMATION ---")
print("Total Records:", df.count())
print("Distinct Hashtags:", df.select("Hashtag").distinct().count())

# Step 3: Group identical hashtags
print("\n--- GROUPED HASHTAGS ---")
grouped = df.groupBy("Hashtag")
grouped.count().orderBy("Hashtag").show(18, truncate=False)

# Step 4: Count hashtag occurrences
print("\n--- HASHTAG OCCURRENCES ---")
hashtag_counts = df.groupBy("Hashtag") \
    .agg(count("*").alias("Occurrences"))

hashtag_counts.orderBy("Hashtag").show(18, truncate=False)

# Step 5: Sort hashtags by popularity
print("\n--- HASHTAGS SORTED BY POPULARITY ---")
popular_hashtags = hashtag_counts.orderBy(
    desc("Occurrences")
)

popular_hashtags.show(18, truncate=False)

# Step 6: Identify top trending hashtags
print("\n--- TOP TRENDING HASHTAGS ---")
popular_hashtags.show(10, truncate=False)

# Step 7: Top 3 hashtags
print("\n--- TOP 3 TRENDING HASHTAGS ---")
popular_hashtags.limit(3).show(truncate=False)

# Step 8: Daily trend analysis
print("\n--- DAILY HASHTAG TRENDS ---")
daily_trends = df.groupBy("Date", "Hashtag") \
    .agg(count("*").alias("Occurrences")) \
    .orderBy("Date", desc("Occurrences"))

daily_trends.show(50, truncate=False)

# Step 9: Regional hashtag analysis
print("\n--- REGIONAL HASHTAG ANALYSIS ---")
regional_trends = df.groupBy("Region", "Hashtag") \
    .agg(count("*").alias("Occurrences")) \
    .orderBy("Region", desc("Occurrences"))

regional_trends.show(50, truncate=False)

# Step 10: Category analysis
print("\n--- CATEGORY-WISE USER INTEREST ---")
category_analysis = df.groupBy("Category") \
    .agg(count("*").alias("Post_Count")) \
    .orderBy(desc("Post_Count"))

category_analysis.show(truncate=False)

spark.stop()
