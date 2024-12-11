from pyspark.sql import SparkSession

from pyspark.sql.functions import (
    col,
    window,
    sum,
    from_json
)

from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType
)

from config import (
    POSTGRES_PASSWORD,
    POSTGRES_USER,
    POSTGRES_URL,
    POSTGRES_TABLE,
    KAFKA_TOPIC,
    KAFKA_SERVERS
)

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
    .option("kafka.bootstrap.servers", KAFKA_SERVERS)
    .option("subscribe", KAFKA_TOPIC)
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
daily_purchase = json_stream.groupBy(
    window(col("timestamp"), "1 day", "1 day").
    alias("day_window"), "furniture"
).agg(sum("purchase_amount").
      alias("total_purchase"))

# Output ke konsol
query_console = (
    daily_purchase.writeStream.outputMode("complete").
    format("console").start()
)

# Output ke PostgreSQL
query_postgres = (
    daily_purchase.writeStream.outputMode("complete")
    .foreachBatch(
        lambda df, epoch_id: df.write.jdbc(
            # Ganti dengan URL PostgreSQL yang sesuai
            url=POSTGRES_URL,
            table=POSTGRES_TABLE,
            mode="append",
            properties={
                "user": POSTGRES_USER,
                "password": POSTGRES_PASSWORD,
            },
        )
    )
    .start()
)

# Menunggu agar query berjalan
query_console.awaitTermination()
query_postgres.awaitTermination()
