#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SmartEdu Analytics - Phase 6: Apache Spark MLlib Machine Learning Pipeline
Script: spark_ml_dropout_prediction.py
Target Environment: Cloudera QuickStart VM (Spark 1.6 / 2.x) & Standard PySpark
Description:
    Trains distributed predictive models to classify student dropout risk:
    1. VectorAssembler for feature extraction
    2. StandardScaler for feature normalization
    3. Model Training: Random Forest Classifier & Logistic Regression
    4. Model Evaluation: ROC-AUC, Accuracy, Precision, Recall, F1-Score
"""

import os
import sys

try:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder \
        .appName("SmartEdu_Spark_ML_Dropout_Prediction") \
        .getOrCreate()
    sc = spark.sparkContext
except ImportError:
    from pyspark import SparkContext
    from pyspark.sql import SQLContext
    sc = SparkContext(appName="SmartEdu_Spark_ML_Dropout_Prediction")
    spark = SQLContext(sc)

from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier, LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator

def main():
    print("=" * 80)
    print(" SmartEdu Analytics - Phase 6: Spark MLlib Dropout Risk Classification")
    print(" Spark Application ID: " + str(sc.applicationId))
    print("=" * 80)

    # Input dataset path
    local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset", "processed", "preprocessed_student_data.csv")
    hdfs_path = "hdfs://quickstart.cloudera:8020/smartedu/processed/preprocessed_student_data.csv"
    input_path = hdfs_path if "quickstart" in os.environ.get("HOSTNAME", "") else (local_path if os.path.exists(local_path) else hdfs_path)

    print("\n[STEP 1] Loading Dataset from: " + input_path)
    df = spark.read.format("csv").option("header", "true").option("inferSchema", "true").load(input_path)

    # Cast feature columns to double
    feature_cols = [
        "admission_grade", "sem1_grade", "sem2_grade", "annual_grade_avg",
        "sem1_units_approved", "sem2_units_approved", "total_units_failed",
        "tuition_fees_up_to_date", "is_debtor", "scholarship_holder",
        "daytime_evening_attendance", "age_at_enrollment"
    ]
    for c in feature_cols:
        df = df.withColumn(c, df[c].cast("double"))
    df = df.withColumn("label", df["is_dropout"].cast("double"))

    # VectorAssembler
    print("\n[STEP 2] Assembling Feature Vector with " + str(len(feature_cols)) + " features...")
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="raw_features")
    assembled_df = assembler.transform(df)

    # StandardScaler
    scaler = StandardScaler(inputCol="raw_features", outputCol="features", withStd=True, withMean=True)
    scaler_model = scaler.fit(assembled_df)
    scaled_df = scaler_model.transform(assembled_df)

    # Train / Test Split (80% Train, 20% Test)
    print("\n[STEP 3] Splitting Dataset into 80% Train and 20% Test...")
    train_df, test_df = scaled_df.randomSplit([0.8, 0.2], seed=42)
    print(" -> Training Instances: " + str(train_df.count()))
    print(" -> Testing Instances : " + str(test_df.count()))

    # Train Model 1: Random Forest Classifier
    print("\n[STEP 4] Training Spark MLlib Random Forest Classifier (numTrees=50, maxDepth=8)...")
    rf = RandomForestClassifier(labelCol="label", featuresCol="features", numTrees=50, maxDepth=8, seed=42)
    rf_model = rf.fit(train_df)
    rf_predictions = rf_model.transform(test_df)

    # Evaluate Model 1
    bin_eval = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
    multi_eval_acc = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    multi_eval_f1 = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")

    rf_auc = bin_eval.evaluate(rf_predictions)
    rf_acc = multi_eval_acc.evaluate(rf_predictions)
    rf_f1 = multi_eval_f1.evaluate(rf_predictions)

    print("\n[EVALUATION: RANDOM FOREST CLASSIFIER]")
    print(" -> Area Under ROC (ROC-AUC) : " + str(round(rf_auc, 4)))
    print(" -> Test Accuracy           : " + str(round(rf_acc * 100, 2)) + "%")
    print(" -> Weighted F1-Score       : " + str(round(rf_f1, 4)))

    # Train Model 2: Logistic Regression (Baseline Comparison)
    print("\n[STEP 5] Training Spark MLlib Logistic Regression Classifier...")
    lr = LogisticRegression(labelCol="label", featuresCol="features", maxIter=20, regParam=0.01)
    lr_model = lr.fit(train_df)
    lr_predictions = lr_model.transform(test_df)

    lr_auc = bin_eval.evaluate(lr_predictions)
    lr_acc = multi_eval_acc.evaluate(lr_predictions)
    lr_f1 = multi_eval_f1.evaluate(lr_predictions)

    print("\n[EVALUATION: LOGISTIC REGRESSION]")
    print(" -> Area Under ROC (ROC-AUC) : " + str(round(lr_auc, 4)))
    print(" -> Test Accuracy           : " + str(round(lr_acc * 100, 2)) + "%")
    print(" -> Weighted F1-Score       : " + str(round(lr_f1, 4)))

    # Feature Importance Analysis (Random Forest)
    print("\n[STEP 6] Random Forest Top Predictive Feature Importances:")
    importances = rf_model.featureImportances.toArray()
    feat_imp = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
    for rank, (feat, imp) in enumerate(feat_imp[:6], start=1):
        print("  Top " + str(rank) + ": " + feat.ljust(25) + " -> Importance: " + str(round(imp, 4)))

    print("\n" + "=" * 80)
    print(" [COMPLETE] Spark MLlib Machine Learning Pipeline Finished Successfully!")
    print("=" * 80)
    sc.stop()

if __name__ == "__main__":
    main()
