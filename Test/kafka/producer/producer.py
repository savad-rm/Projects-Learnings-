# from kafka import KafkaProducer


# TOPIC_NAME='test'
# KAFKA_SERVER='localhost:9092'

# producer=KafkaProducer(bootstrap_servers=KAFKA_SERVER)

# producer.send(TOPIC_NAME,b'Test Message!!!')
# producer.flush()

from confluent_kafka import Producer

TOPIC_NAME = 'test'
KAFKA_SERVER = 'localhost:9092'

# Configuration options
conf = {
    'bootstrap.servers': KAFKA_SERVER,
}

# Create Kafka producer instance
producer = Producer(conf)

# Produce a test message
producer.produce(TOPIC_NAME, key=None, value='Test Message!!!')

# Wait for any outstanding messages to be delivered and delivery reports received
producer.flush()
