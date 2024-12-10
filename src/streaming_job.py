from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, sum, from_json
from pyspark.sql.types import StructType, StructField, StringType, IntegerType  # Add StructField here

# Inisialisasi SparkSession
spark = SparkSession.builder.appName("KafkaStreamingJob").getOrCreate()

# Definisikan schema untuk data JSON
schema = StructType(
    [
        StructField("furniture", StringType(), True),
        StructField("purchase_amount", IntegerType(), True),
        StructField("timestamp", IntegerType(), True),
    ]
)

# Membaca data dari Kafka
kafka_stream = (
    spark.readStream.format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "purchase_topic")
    .load()
)

# Mengubah nilai Kafka ke format JSON
json_stream = (
    kafka_stream.selectExpr("CAST(value AS STRING)")
    .select(from_json("value", schema).alias("data"))
    .select("data.*")
)

# Agregasi pembelian harian
daily_purchase = json_stream.groupBy(
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
            # Ganti dengan URL PostgreSQL yang sesuai
            url="jdbc:postgresql://postgres:5432/dbname",
            table="purchase_summary",
            mode="append",
            properties={
                "user": "username",
                "password": "password",
            },  # Ganti dengan kredensial yang sesuai
        )
    )
    .start()
)

# Menunggu agar query berjalan
query_console.awaitTermination()
query_postgres.awaitTermination()
