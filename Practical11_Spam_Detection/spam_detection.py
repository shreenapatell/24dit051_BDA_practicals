
import os
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml import Pipeline
from pyspark.ml.feature import (
    StringIndexer,
    RegexTokenizer,
    StopWordsRemover,
    HashingTF,
    IDF
)
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import (
    MulticlassClassificationEvaluator,
    BinaryClassificationEvaluator
)
from pyspark.ml.functions import vector_to_array

# --------------------------------------------------
# 1. CREATE SPARK SESSION
# --------------------------------------------------

spark = (
    SparkSession.builder
    .appName("SMS Spam Detection")
    .master("local[*]")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

print("\n========== SMS SPAM DETECTION ==========")

# --------------------------------------------------
# 2. LOAD DATASET FROM HDFS OR LOCAL CSV
# --------------------------------------------------

hdfs_path = "hdfs://localhost:9000/user/student/sms_spam_large.csv"
local_path = "sms_spam.csv"

if os.path.exists(local_path):
    data_path = local_path
    print("Loading dataset from local CSV:", local_path)
else:
    data_path = hdfs_path
    print("Loading dataset from HDFS:", hdfs_path)

df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(data_path)
)

# Standardize the expected column names
if "label" not in df.columns or "message_text" not in df.columns:
    raise ValueError(
        "CSV must contain columns named 'label' and 'message_text'. "
        f"Found: {df.columns}"
    )

df = (
    df.select("label", "message_text")
    .dropna()
    .withColumn("label", F.lower(F.trim(F.col("label"))))
    .withColumn("message_text", F.trim(F.col("message_text")))
    .filter(F.col("message_text") != "")
    .filter(F.col("label").isin("ham", "spam"))
)

print("\n========== DATASET INFORMATION ==========")
print("Total records:", df.count())
df.printSchema()
df.groupBy("label").count().show()

# --------------------------------------------------
# 3. LABEL INDEXING
# Ensure ham = 0 and spam = 1
# --------------------------------------------------

label_indexer = StringIndexer(
    inputCol="label",
    outputCol="labelIndex",
    stringOrderType="alphabetAsc"
)

# Alphabetic order: ham = 0, spam = 1
# Confirm this mapping from the indexed data.
indexed = label_indexer.fit(df).transform(df)

print("Label mapping: ham = 0.0, spam = 1.0")
indexed.groupBy("label", "labelIndex").count().show()

# --------------------------------------------------
# 4. TRAIN-TEST SPLIT
# --------------------------------------------------

train, test = indexed.randomSplit([0.8, 0.2], seed=42)

train = train.cache()
test = test.cache()

train_count = train.count()
test_count = test.count()

if train_count == 0 or test_count == 0:
    raise ValueError("Training or test dataset is empty.")

print("Training records:", train_count)
print("Testing records:", test_count)

# --------------------------------------------------
# 5. TEXT PREPROCESSING AND TF-IDF
# --------------------------------------------------

tokenizer = RegexTokenizer(
    inputCol="message_text",
    outputCol="tokens",
    pattern="\\W+",
    toLowercase=True
)

stop_words = StopWordsRemover(
    inputCol="tokens",
    outputCol="filteredTokens"
)

hashing_tf = HashingTF(
    inputCol="filteredTokens",
    outputCol="rawFeatures",
    numFeatures=4096
)

idf = IDF(
    inputCol="rawFeatures",
    outputCol="features"
)

# --------------------------------------------------
# 6. TRAIN LOGISTIC REGRESSION MODEL
# --------------------------------------------------

lr = LogisticRegression(
    featuresCol="features",
    labelCol="labelIndex",
    maxIter=50,
    regParam=0.01,
    elasticNetParam=0.0
)

pipeline = Pipeline(
    stages=[tokenizer, stop_words, hashing_tf, idf, lr]
)

print("\n========== MODEL TRAINING ==========")

start = time.time()
model = pipeline.fit(train)
training_time = time.time() - start

print(f"Training time: {training_time:.2f} seconds")

# --------------------------------------------------
# 7. MODEL EVALUATION
# --------------------------------------------------

predictions = model.transform(test).cache()

predictions.select(
    "label", "message_text", "labelIndex",
    "prediction", "probability"
).show(10, truncate=False)

# Spam is class index 1.0 because alphabetic ordering
# places ham before spam.
spam_index = 1.0

tp = predictions.filter(
    (F.col("labelIndex") == spam_index) &
    (F.col("prediction") == spam_index)
).count()

tn = predictions.filter(
    (F.col("labelIndex") == 0.0) &
    (F.col("prediction") == 0.0)
).count()

fp = predictions.filter(
    (F.col("labelIndex") == 0.0) &
    (F.col("prediction") == spam_index)
).count()

fn = predictions.filter(
    (F.col("labelIndex") == spam_index) &
    (F.col("prediction") == 0.0)
).count()

accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) else 0
precision = tp / (tp + fp) if (tp + fp) else 0
recall = tp / (tp + fn) if (tp + fn) else 0
f1 = (
    2 * precision * recall / (precision + recall)
    if (precision + recall) else 0
)

auc_evaluator = BinaryClassificationEvaluator(
    labelCol="labelIndex",
    rawPredictionCol="rawPrediction",
    metricName="areaUnderROC"
)

auc = auc_evaluator.evaluate(predictions)

print("\n========== EVALUATION METRICS ==========")
print(f"True Positives: {tp}")
print(f"True Negatives: {tn}")
print(f"False Positives: {fp}")
print(f"False Negatives: {fn}")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"ROC-AUC:   {auc:.4f}")

# --------------------------------------------------
# 8. HYPERPARAMETER TUNING
# --------------------------------------------------

print("\n========== HYPERPARAMETER TUNING ==========")

for reg in [0.0, 0.01, 0.1]:
    for elastic in [0.0, 0.5, 1.0]:
        tuning_lr = LogisticRegression(
            featuresCol="features",
            labelCol="labelIndex",
            maxIter=30,
            regParam=reg,
            elasticNetParam=elastic
        )

        tuning_pipeline = Pipeline(
            stages=[
                tokenizer,
                stop_words,
                hashing_tf,
                idf,
                tuning_lr
            ]
        )

        start = time.time()
        tuning_model = tuning_pipeline.fit(train)
        tuning_predictions = tuning_model.transform(test)

        tuning_accuracy = MulticlassClassificationEvaluator(
            labelCol="labelIndex",
            predictionCol="prediction",
            metricName="accuracy"
        ).evaluate(tuning_predictions)

        elapsed = time.time() - start

        print(
            f"regParam={reg}, elasticNetParam={elastic}, "
            f"maxIter=30, accuracy={tuning_accuracy:.4f}, "
            f"time={elapsed:.2f}s"
        )

# --------------------------------------------------
# 9. DATASET-SIZE EXPERIMENT
# --------------------------------------------------

print("\n========== DATASET SIZE EXPERIMENT ==========")

for fraction in [0.25, 0.5, 1.0]:
    sample = train.sample(
        withReplacement=False,
        fraction=fraction,
        seed=42
    ).cache()

    sample_count = sample.count()

    if sample_count == 0:
        print(f"Skipping fraction={fraction}: no records sampled")
        sample.unpersist()
        continue

    size_lr = LogisticRegression(
        featuresCol="features",
        labelCol="labelIndex",
        maxIter=30,
        regParam=0.01,
        elasticNetParam=0.0
    )

    size_pipeline = Pipeline(
        stages=[
            tokenizer,
            stop_words,
            hashing_tf,
            idf,
            size_lr
        ]
    )

    start = time.time()
    size_model = size_pipeline.fit(sample)
    elapsed = time.time() - start

    size_predictions = size_model.transform(test)

    size_accuracy = MulticlassClassificationEvaluator(
        labelCol="labelIndex",
        predictionCol="prediction",
        metricName="accuracy"
    ).evaluate(size_predictions)

    print(
        f"Training records={sample_count}, "
        f"training time={elapsed:.2f}s, "
        f"accuracy={size_accuracy:.4f}"
    )

    sample.unpersist()

# --------------------------------------------------
# 10. SPAM THRESHOLD ANALYSIS
# --------------------------------------------------

print("\n========== SPAM THRESHOLD ANALYSIS ==========")

probability_predictions = predictions.withColumn(
    "spamProbability",
    vector_to_array(F.col("probability"))[1]
)

actual_spam_count = predictions.filter(
    F.col("labelIndex") == spam_index
).count()

for threshold in [0.3, 0.5, 0.7]:
    threshold_predictions = probability_predictions.withColumn(
        "thresholdPrediction",
        (F.col("spamProbability") >= threshold).cast("double")
    )

    threshold_tp = threshold_predictions.filter(
        (F.col("labelIndex") == spam_index) &
        (F.col("thresholdPrediction") == 1.0)
    ).count()

    threshold_fp = threshold_predictions.filter(
        (F.col("labelIndex") == 0.0) &
        (F.col("thresholdPrediction") == 1.0)
    ).count()

    threshold_fn = threshold_predictions.filter(
        (F.col("labelIndex") == spam_index) &
        (F.col("thresholdPrediction") == 0.0)
    ).count()

    threshold_recall = (
        threshold_tp / (threshold_tp + threshold_fn)
        if (threshold_tp + threshold_fn) else 0
    )

    threshold_precision = (
        threshold_tp / (threshold_tp + threshold_fp)
        if (threshold_tp + threshold_fp) else 0
    )

    print(
        f"Threshold={threshold:.1f}, "
        f"Precision={threshold_precision:.4f}, "
        f"Recall={threshold_recall:.4f}"
    )

# --------------------------------------------------
# 11. SAVE PREDICTIONS
# --------------------------------------------------


print("\n========== SAVING PREDICTIONS ==========")

output_path = "spam_predictions_output"

(
    predictions
    .withColumn(
        "spamProbability",
        vector_to_array(F.col("probability"))[1]
    )
    .select(
        "label",
        "message_text",
        "prediction",
        "spamProbability"
    )
    .write
    .mode("overwrite")
    .option("header", True)
    .csv(output_path)
)

print("Predictions saved to:", output_path)
print("\nPractical 11 completed.")

predictions.unpersist()
train.unpersist()
test.unpersist()
spark.stop()
