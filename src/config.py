# config.py

# Kafka Configurations
KAFKA_SERVERS = 'localhost:9092'  # Alamat Kafka server
KAFKA_TOPIC = 'purchase_topic'    # Nama topik Kafka yang digunakan

# PostgreSQL Configurations
POSTGRES_URL = 'jdbc:postgresql://localhost:5432/dbname'  # Ganti dengan URL PostgreSQL
POSTGRES_TABLE = 'purchase_summary'  # Nama tabel di PostgreSQL untuk menyimpan hasil agregasi
POSTGRES_USER = 'username'           # Username untuk koneksi ke PostgreSQL
POSTGRES_PASSWORD = 'password'       # Password untuk koneksi ke PostgreSQL
