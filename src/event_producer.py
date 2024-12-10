from confluent_kafka import Producer
import json
import time
from random import randint
import signal
import sys


# Fungsi callback untuk laporan pengiriman pesan
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# Inisialisasi Kafka producer
producer = Producer(
    # Ganti dengan server Kafka yang digunakan
    {"bootstrap.servers": "kafka:9092"}
)

# Daftar furniture yang dapat dipilih
furnitures = ["Chair", "Table", "Sofa", "Desk", "Lamp"]


# Fungsi untuk mengirim event pembelian ke Kafka
def send_purchase_event():
    while True:
        # Pilih furnitur secara acak dan tentukan nilai pembelian
        furniture = furnitures[randint(0, len(furnitures) - 1)]
        purchase_amount = randint(100, 1000)

        # Membuat event pembelian
        event = {
            "furniture": furniture,
            "purchase_amount": purchase_amount,
            # Waktu saat event dibuat (epoch time)
            "timestamp": int(time.time()),
        }

        # Mengirim event ke Kafka
        producer.produce(
            "purchase_topic",
            key=furniture,
            value=json.dumps(event),
            callback=delivery_report,
        )
        # Poll the producer to handle callbacks
        producer.poll(0)

        # Delay pengiriman event agar tidak terlalu cepat
        time.sleep(1)


# Gracefully shut down the producer on SIGINT (Ctrl+C)
def graceful_shutdown(signal, frame):
    print("Gracefully shutting down...")
    producer.flush()  # Ensure all messages are delivered before shutting down
    sys.exit(0)


# Attach the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, graceful_shutdown)

# Start sending events
send_purchase_event()
