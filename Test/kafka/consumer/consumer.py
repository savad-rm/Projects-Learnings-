# from kafka import KafkaConsumer

# TOPIC_NAME='test'

# consumer=KafkaConsumer(TOPIC_NAME)
# for message in consumer:
#     print(message)

from confluent_kafka import Consumer, KafkaError

TOPIC_NAME = 'test'
KAFKA_SERVER = 'localhost:9092'

# Configuration options
conf = {
    'bootstrap.servers': KAFKA_SERVER,
    'group.id': 'my_consumer_group',  # Specify your consumer group ID
    'auto.offset.reset': 'earliest',  # Start reading from the beginning of the topic
}

# Create Kafka consumer instance
consumer = Consumer(conf)

# Subscribe to the topic
consumer.subscribe([TOPIC_NAME])

# Poll for messages
try:
    while True:
        msg = consumer.poll(1.0)  # Timeout in seconds

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f"Reached end of partition {msg.partition()}")
            else:
                print(f"Error: {msg.error()}")
        else:
            # Print the received message
            print(f"Received message: {msg.value().decode('utf-8')}")

except KeyboardInterrupt:
    pass
finally:
    # Close down consumer to commit final offsets.
    consumer.close()
