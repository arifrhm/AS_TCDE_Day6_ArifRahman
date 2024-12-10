from confluent_kafka import Producer
import json
import time
from random import randint


# Fungsi callback untuk laporan pengiriman pesan
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# Inisialisasi Kafka producer
producer = Producer(
    {"bootstrap.servers": "localhost:9092"}
)  # Ganti dengan server Kafka yang digunakan

# Daftar furniture yang dapat dipilih
furnitures = ["Chair", "Table", "Sofa", "Desk", "Lamp"]

# Fungsi untuk mengirim event pembelian ke Kafka
while True:
    # Pilih furnitur secara acak dan tentukan nilai pembelian
    furniture = furnitures[randint(0, len(furnitures) - 1)]
    purchase_amount = randint(100, 1000)

    # Membuat event pembelian
    event = {
        "furniture": furniture,
        "purchase_amount": purchase_amount,
        "timestamp": int(time.time()),  # Waktu saat event dibuat (epoch time)
    }

    # Mengirim event ke Kafka
    producer.produce(
        "purchase_topic",
        key=furniture,
        value=json.dumps(event),
        callback=delivery_report,
    )
    producer.flush()  # Pastikan pesan terkirim

    # Delay pengiriman event agar tidak terlalu cepat
    time.sleep(1)
