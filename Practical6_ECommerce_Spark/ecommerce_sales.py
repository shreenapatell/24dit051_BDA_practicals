from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, month, trim


# Create Spark session
spark = SparkSession.builder \
    .appName("ECommerceSalesAnalysis") \
    .master("local[*]") \
    .getOrCreate()


# Load sales data
df = spark.read.csv(
    "sales_data.csv",
    header=True,
    inferSchema=True
)


# Clean city names
df = df.withColumn("City", trim(col("City")))


# Display dataset
print("\n--- Sales Data ---")
df.show()


# Display schema
print("\n--- Dataset Schema ---")
df.printSchema()


# Validate data types
print("\n--- Column Data Types ---")
for column, datatype in df.dtypes:
    print(column, ":", datatype)


# Create Revenue column
df = df.withColumn(
    "Revenue",
    col("Quantity") * col("Price")
)

print("\n--- Revenue Calculation ---")
df.show()


# Category-wise revenue
category_revenue = df.groupBy("Category") \
    .agg(
        sum("Revenue").alias("Total_Revenue")
    ) \
    .orderBy(
        col("Total_Revenue").desc()
    )

print("\n--- Category-wise Revenue ---")
category_revenue.show()


# Top-selling products based on quantity
top_products = df.groupBy("Product") \
    .agg(
        sum("Quantity").alias("Total_Quantity_Sold")
    ) \
    .orderBy(
        col("Total_Quantity_Sold").desc()
    )

print("\n--- Top-Selling Products ---")
top_products.show()


# City-wise revenue
city_revenue = df.groupBy("City") \
    .agg(
        sum("Revenue").alias("Total_Revenue")
    ) \
    .orderBy(
        col("Total_Revenue").desc()
    )

print("\n--- City-wise Revenue ---")
city_revenue.show()


# Average revenue per order
average_revenue = df.select(
    avg("Revenue").alias("Average_Revenue_Per_Order")
)

print("\n--- Average Revenue Per Order ---")
average_revenue.show()


# Top 3 revenue-generating cities
print("\n--- Top 3 Revenue-Generating Cities ---")
city_revenue.limit(3).show()


# Add discount amount
df = df.withColumn(
    "Discount_Amount",
    col("Revenue") * col("Discount") / 100
)


# Calculate net revenue
df = df.withColumn(
    "Net_Revenue",
    col("Revenue") - col("Discount_Amount")
)

print("\n--- Discounted Revenue ---")
df.select(
    "OrderID",
    "Product",
    "Revenue",
    "Discount",
    "Discount_Amount",
    "Net_Revenue"
).show()


# Least-performing category
print("\n--- Least-Performing Category ---")
category_revenue \
    .orderBy(col("Total_Revenue").asc()) \
    .limit(1) \
    .show()


# Monthly revenue
monthly_revenue = df.groupBy(
    month("OrderDate").alias("Month")
).agg(
    sum("Revenue").alias("Monthly_Revenue")
).orderBy("Month")

print("\n--- Monthly Revenue ---")
monthly_revenue.show()


# Stop Spark
spark.stop()
