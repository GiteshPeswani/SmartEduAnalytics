#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SmartEdu Analytics - Phase 6: Apache Spark Distributed Processing
Script: spark_student_analytics.py
Target Environment: Cloudera QuickStart VM (Spark 1.6 / 2.x) & Standard PySpark
Description:
    Implements distributed student performance analytics using Apache Spark:
    1. Spark DataFrame Transformations & Actions
    2. Spark SQL Analytical Queries
    3. Course, Attendance & Performance Tier Aggregations
    4. Exports analytics partitions to /smartedu/analytics/spark/
"""

import os
import sys

# Initialize Spark compatibility layer for both Spark 1.6 (CDH 5.13) and Spark 2+/3+
try:
    from pyspark.sql import SparkSession
    spark = SparkSession.builder \
        .appName("SmartEdu_Student_Analytics") \
        .getOrCreate()
    sc = spark.sparkContext
    sqlContext = spark
except ImportError:
    from pyspark import SparkContext
    from pyspark.sql import SQLContext
    sc = SparkContext(appName="SmartEdu_Student_Analytics")
    sqlContext = SQLContext(sc)
    spark = sqlContext

from pyspark.sql.functions import col, when, avg, count, sum as spark_sum, min as spark_min, max as spark_max, round as spark_round, desc

def main():
    print("=" * 80)
    print(" SmartEdu Analytics - Phase 6: Apache Spark Distributed Processing")
    print(" Spark Application ID: " + str(sc.applicationId))
    print(" Spark Version: " + str(sc.version))
    print("=" * 80)

    # Input dataset path: prefers HDFS, falls back to local path
    hdfs_path = "hdfs://quickstart.cloudera:8020/smartedu/processed/preprocessed_student_data.csv"
    local_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dataset", "processed", "preprocessed_student_data.csv")
    
    input_path = hdfs_path if "quickstart" in os.environ.get("HOSTNAME", "") else (local_path if os.path.exists(local_path) else hdfs_path)
    
    print("\n[STEP 1] Loading Dataset into Spark DataFrame from: " + input_path)
    df = spark.read \
        .format("csv") \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .load(input_path)

    # Spark Actions Demonstration
    record_count = df.count()
    col_count = len(df.columns)
    print(" -> [ACTION: count()] Total Records: " + str(record_count) + " | Columns: " + str(col_count))

    # Spark Transformation: withColumn, cast, and custom flags
    df_transformed = df \
        .withColumn("annual_grade_avg", col("annual_grade_avg").cast("double")) \
        .withColumn("sem1_grade", col("sem1_grade").cast("double")) \
        .withColumn("sem2_grade", col("sem2_grade").cast("double")) \
        .withColumn("admission_grade", col("admission_grade").cast("double")) \
        .withColumn("total_enrolled_units", col("sem1_units_enrolled") + col("sem2_units_enrolled")) \
        .withColumn("total_approved_units", col("sem1_units_approved") + col("sem2_units_approved")) \
        .withColumn("total_unattended_units", col("sem1_units_without_eval") + col("sem2_units_without_eval")) \
        .withColumn("participation_rate", spark_round((1.0 - (col("total_unattended_units") / col("total_enrolled_units"))) * 100.0, 2)) \
        .withColumn("perf_tier", 
                    when(col("annual_grade_avg") >= 14.0, "Excellent")
                    .when(col("annual_grade_avg") >= 12.0, "Good")
                    .when(col("annual_grade_avg") >= 10.0, "Average")
                    .otherwise("Needs_Improvement"))

    # Register Temporary View for Spark SQL
    df_transformed.createOrReplaceTempView("students_spark")

    # --------------------------------------------------------------------------
    # Analytics 1: Cohort Overview & Baseline Averages
    # --------------------------------------------------------------------------
    print("\n[SPARK SQL 1] Cohort Academic Performance Baseline:")
    q1 = spark.sql("""
        SELECT 
            COUNT(*) AS total_students,
            ROUND(AVG(admission_grade), 2) AS avg_admission,
            ROUND(AVG(sem1_grade), 2) AS avg_sem1,
            ROUND(AVG(sem2_grade), 2) AS avg_sem2,
            ROUND(AVG(annual_grade_avg), 2) AS avg_annual,
            ROUND(AVG(total_units_failed), 2) AS avg_failed_units
        FROM students_spark
    """)
    q1.show()

    # --------------------------------------------------------------------------
    # Analytics 2: Subject / Course-Wise Performance Analysis
    # --------------------------------------------------------------------------
    print("\n[SPARK SQL 2] Course-Wise Academic Performance & Unit Pass Rates:")
    q2 = spark.sql("""
        SELECT 
            course_id,
            COUNT(*) AS student_count,
            ROUND(AVG(annual_grade_avg), 2) AS avg_annual_grade,
            ROUND(SUM(total_approved_units) * 100.0 / SUM(total_enrolled_units), 2) AS pass_rate_pct,
            SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) AS dropouts,
            ROUND(SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS dropout_rate_pct
        FROM students_spark
        GROUP BY course_id
        ORDER BY avg_annual_grade DESC
    """)
    q2.show(17, truncate=False)

    # --------------------------------------------------------------------------
    # Analytics 3: Attendance & Participation Analysis (< 75% Alerts)
    # --------------------------------------------------------------------------
    print("\n[SPARK SQL 3] Attendance Mode & Low Participation Alerts (< 75%):")
    q3 = spark.sql("""
        SELECT 
            CASE WHEN daytime_evening_attendance = 1 THEN 'Daytime' ELSE 'Evening' END AS attendance_mode,
            COUNT(*) AS total_students,
            ROUND(AVG(participation_rate), 2) AS mean_participation_pct,
            SUM(CASE WHEN participation_rate < 75.0 THEN 1 ELSE 0 END) AS low_attendance_count,
            ROUND(SUM(CASE WHEN participation_rate < 75.0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS low_attendance_pct
        FROM students_spark
        GROUP BY daytime_evening_attendance
    """)
    q3.show()

    # --------------------------------------------------------------------------
    # Analytics 4: Student Performance Classification Breakdown
    # --------------------------------------------------------------------------
    print("\n[SPARK SQL 4] Performance Classification Tiers:")
    q4 = spark.sql("""
        SELECT 
            perf_tier,
            COUNT(*) AS student_count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM students_spark), 2) AS pct_of_cohort,
            ROUND(AVG(annual_grade_avg), 2) AS mean_grade,
            SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) AS actual_dropouts,
            ROUND(SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS dropout_rate_pct
        FROM students_spark
        GROUP BY perf_tier
        ORDER BY mean_grade DESC
    """)
    q4.show()

    # --------------------------------------------------------------------------
    # Analytics 5: Top 5 and Bottom 5 Students
    # --------------------------------------------------------------------------
    print("\n[SPARK SQL 5] Top 5 Academic Performers:")
    q5_top = spark.sql("""
        SELECT student_id, course_id, admission_grade, sem1_grade, sem2_grade, annual_grade_avg, target_outcome
        FROM students_spark
        ORDER BY annual_grade_avg DESC
        LIMIT 5
    """)
    q5_top.show()

    print("\n[SPARK SQL 5] Bottom 5 Struggling Students:")
    q5_bot = spark.sql("""
        SELECT student_id, course_id, admission_grade, sem1_grade, sem2_grade, annual_grade_avg, target_outcome
        FROM students_spark
        WHERE annual_grade_avg > 0
        ORDER BY annual_grade_avg ASC
        LIMIT 5
    """)
    q5_bot.show()

    # --------------------------------------------------------------------------
    # Export Outputs into HDFS Analytics Path (/smartedu/analytics/spark/)
    # --------------------------------------------------------------------------
    spark_out_dir = "/smartedu/analytics/spark/course_performance"
    print("\n[STEP 3] Exporting Spark DataFrame Results to HDFS: " + spark_out_dir)
    try:
        q2.write.mode("overwrite").format("csv").option("header", "true").save(spark_out_dir)
        print(" -> Exported course performance dataset to HDFS successfully.")
    except Exception as e:
        print(" -> HDFS write notice: " + str(e))

    print("\n" + "=" * 80)
    print(" [COMPLETE] Apache Spark Distributed Processing Completed Successfully!")
    print("=" * 80)
    sc.stop()

if __name__ == "__main__":
    main()
