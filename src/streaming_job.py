from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, sum, from_json, from_unixtime
from pyspark.sql.types import StructType, StructField, StringType, LongType, IntegerType

# Inisialisasi SparkSession dengan Kafka Connector
spark = SparkSession.builder \
    .appName("KafkaStreamingJob") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .getOrCreate()

# Definisikan schema untuk data JSON
schema = StructType(
    [
        StructField("furniture", StringType(), True),
        StructField("purchase_amount", IntegerType(), True),
        StructField("timestamp", LongType(), True),  # Use LongType for Unix timestamp
    ]
)

# Membaca data dari Kafka
kafka_stream = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")  # Use the Docker service name 'kafka' here
    .option("subscribe", "purchase_topic")
    .load()
)

# Mengubah nilai Kafka ke format JSON
json_stream = (
    kafka_stream.selectExpr("CAST(value AS STRING)")
    .select(from_json("value", schema).alias("data"))
    .select("data.*")
)

# Convert timestamp (BigInt) to proper Timestamp
json_stream_with_timestamp = json_stream.withColumn(
    "timestamp", from_unixtime(col("timestamp") / 1000).cast("timestamp")  # Convert from BigInt to Timestamp
)

# Agregasi pembelian harian
daily_purchase = json_stream_with_timestamp.groupBy(
    window(col("timestamp"), "1 day", "1 day").alias("day_window"), "furniture"
).agg(sum("purchase_amount").alias("total_purchase"))

# Output ke konsol
query_console = (
    daily_purchase.writeStream.outputMode("complete").format("console").start()
)

# Output ke PostgreSQL
query_postgres = (
    daily_purchase.writeStream.outputMode("complete")
    .foreachBatch(
        lambda df, epoch_id: df.write.jdbc(
            url="jdbc:postgresql://postgres:5432/dbname",  # Make sure this is correct
            table="purchase_summary",
            mode="append",
            properties={
                "user": "username",  # Replace with your username
                "password": "password",  # Replace with your password
            }
        )
    )
    .start()
)

# Menunggu agar query berjalan
query_console.awaitTermination()
query_postgres.awaitTermination()
