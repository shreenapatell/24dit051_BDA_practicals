from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum, count, avg, max, lit, datediff, to_date
)
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans

spark = SparkSession.builder \
    .appName("KMeansElbowMethod") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

df = spark.read.csv(
    "customer_transactions.csv",
    header=True,
    inferSchema=True
)

features = df.groupBy("CustomerID").agg(
    sum("Amount").alias("TotalSpend"),
    count("*").alias("PurchaseFrequency"),
    avg("Amount").alias("AverageBasketSize"),
    max("Date").alias("LastPurchaseDate")
)

features = features.withColumn(
    "Recency",
    datediff(
        to_date(lit("2026-07-01")),
        to_date(col("LastPurchaseDate"))
    )
)

assembler = VectorAssembler(
    inputCols=[
        "TotalSpend",
        "PurchaseFrequency",
        "AverageBasketSize",
        "Recency"
    ],
    outputCol="features"
)

assembled = assembler.transform(features)

scaler = StandardScaler(
    inputCol="features",
    outputCol="scaledFeatures",
    withStd=True,
    withMean=True
)

scaled = scaler.fit(assembled).transform(assembled)

print("\n--- ELBOW METHOD ---")

for k in range(2, 9):
    kmeans = KMeans(
        featuresCol="scaledFeatures",
        predictionCol="Cluster",
        k=k,
        seed=42
    )

    model = kmeans.fit(scaled)

    print("k =", k, " WSSSE =", model.summary.trainingCost)

spark.stop()
