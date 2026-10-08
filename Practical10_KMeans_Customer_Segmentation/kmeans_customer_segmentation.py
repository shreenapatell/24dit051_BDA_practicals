from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    sum,
    count,
    avg,
    max,
    lit,
    datediff,
    to_date
)
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

# --------------------------------------------------
# Create Spark Session
# --------------------------------------------------

spark = SparkSession.builder \
    .appName("ParallelKMeansCustomerSegmentation") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --------------------------------------------------
# Step 1: Load Customer Transaction Dataset
# --------------------------------------------------

df = spark.read.csv(
    "customer_transactions.csv",
    header=True,
    inferSchema=True
)

print("\n--- CUSTOMER TRANSACTION DATA ---")
df.show(20, truncate=False)

# --------------------------------------------------
# Step 2: Validate Dataset Structure
# --------------------------------------------------

print("\n--- DATASET SCHEMA ---")
df.printSchema()

print("\n--- DATASET INFORMATION ---")
print("Total Transactions:", df.count())
print("Unique Customers:", df.select("CustomerID").distinct().count())

# --------------------------------------------------
# Step 3: Extract Customer Behavioural Features
# --------------------------------------------------

customer_features = df.groupBy("CustomerID").agg(
    sum("Amount").alias("TotalSpend"),
    count("*").alias("PurchaseFrequency"),
    avg("Amount").alias("AverageBasketSize"),
    max("Date").alias("LastPurchaseDate")
)

# --------------------------------------------------
# Calculate Recency
# --------------------------------------------------

reference_date = "2026-07-01"

customer_features = customer_features.withColumn(
    "Recency",
    datediff(
        to_date(lit(reference_date)),
        to_date(col("LastPurchaseDate"))
    )
)

print("\n--- CUSTOMER BEHAVIOURAL FEATURES ---")

customer_features.select(
    "CustomerID",
    "TotalSpend",
    "PurchaseFrequency",
    "AverageBasketSize",
    "LastPurchaseDate",
    "Recency"
).orderBy("CustomerID").show(20, truncate=False)

# --------------------------------------------------
# Step 4: Assemble Features
# --------------------------------------------------

assembler = VectorAssembler(
    inputCols=[
        "TotalSpend",
        "PurchaseFrequency",
        "AverageBasketSize",
        "Recency"
    ],
    outputCol="features"
)

assembled = assembler.transform(customer_features)

print("\n--- ASSEMBLED FEATURES ---")

assembled.select(
    "CustomerID",
    "features"
).show(10, truncate=False)

# --------------------------------------------------
# Step 5: Normalize Features Using StandardScaler
# --------------------------------------------------

scaler = StandardScaler(
    inputCol="features",
    outputCol="scaledFeatures",
    withStd=True,
    withMean=True
)

scaler_model = scaler.fit(assembled)

scaled_data = scaler_model.transform(assembled)

print("\n--- NORMALIZED CUSTOMER FEATURES ---")

scaled_data.select(
    "CustomerID",
    "TotalSpend",
    "PurchaseFrequency",
    "AverageBasketSize",
    "Recency",
    "scaledFeatures"
).show(10, truncate=False)

# --------------------------------------------------
# Step 6: Apply K-Means Clustering
# --------------------------------------------------

kmeans = KMeans(
    featuresCol="scaledFeatures",
    predictionCol="Cluster",
    k=5,
    seed=42
)

model = kmeans.fit(scaled_data)

predictions = model.transform(scaled_data)

print("\n--- K-MEANS CUSTOMER CLUSTERS ---")

predictions.select(
    "CustomerID",
    "TotalSpend",
    "PurchaseFrequency",
    "AverageBasketSize",
    "Recency",
    "Cluster"
).orderBy(
    "Cluster",
    "CustomerID"
).show(100, truncate=False)

# --------------------------------------------------
# Step 7: Calculate WSSSE
# --------------------------------------------------

wssse = model.summary.trainingCost

print("\n--- CLUSTERING EVALUATION ---")
print("WSSSE:", wssse)

# --------------------------------------------------
# Step 8: Calculate Silhouette Score
# --------------------------------------------------

evaluator = ClusteringEvaluator(
    featuresCol="scaledFeatures",
    predictionCol="Cluster",
    metricName="silhouette"
)

silhouette = evaluator.evaluate(predictions)

print("Silhouette Score:", silhouette)

# --------------------------------------------------
# Step 9: Customer Segment Summary
# --------------------------------------------------

print("\n--- CUSTOMER SEGMENT SUMMARY ---")

cluster_summary = predictions.groupBy("Cluster").agg(
    count("*").alias("Customers"),
    avg("TotalSpend").alias("AvgSpend"),
    avg("PurchaseFrequency").alias("AvgFrequency"),
    avg("AverageBasketSize").alias("AvgBasket"),
    avg("Recency").alias("AvgRecency")
).orderBy("Cluster")

cluster_summary.show(truncate=False)

# --------------------------------------------------
# Stop Spark
# --------------------------------------------------

spark.stop()
