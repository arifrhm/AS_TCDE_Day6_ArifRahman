# config.py

# Kafka Configurations
KAFKA_SERVERS = "kafka:9092"  # Alamat Kafka server
KAFKA_TOPIC = "purchase_topic"  # Nama topik Kafka yang digunakan

# PostgreSQL Configurations
# Ganti dengan URL PostgreSQL
POSTGRES_URL = "jdbc:postgresql://postgres:5432/dbname"
# Nama tabel di PostgreSQL untuk menyimpan hasil agregasi
POSTGRES_TABLE = "purchase_summary"

# Username untuk koneksi ke PostgreSQL
POSTGRES_USER = "username"
# Password untuk koneksi ke PostgreSQL
POSTGRES_PASSWORD = "password"
