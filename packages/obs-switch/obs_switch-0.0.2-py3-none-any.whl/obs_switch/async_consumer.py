import sys
import json
from confluent_kafka import Consumer, KafkaError, KafkaException
from typing import List, Callable


class AsyncConsumer:
    """Asynchronous Kafka consumer for handling messages"""
    
    def __init__(self, bootstrap_servers: str = '127.0.0.1:9092', group_id: str = 'replayservice'):
        """Initialize the Kafka consumer with configuration"""
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'enable.auto.commit': 'true'
        }
        self.consumer = Consumer(self.conf)
        self.running = True
    
    def default_message_processor(self, message):
        """Default message processor that prints the message key and value"""
        print(f"Message - {message.key().decode('utf-8')}")
        print(json.loads(message.value()))
    
    def basic_consumer_loop(self, topics: List[str], processor: Callable = None):
        """Basic consumption loop with default message processor"""
        if processor is None:
            processor = self.default_message_processor
            
        try:
            self.consumer.subscribe(topics)

            while self.running:
                msg = self.consumer.poll(timeout=0.2)
                if msg is None: 
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                        (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    processor(msg)
        except Exception as e:
            print(f"Error in consume loop: {e}")
        finally:
            # Close down consumer to commit final offsets.
            self.consumer.close()
    
    def custom_consumer_loop(self, topics: List[str], callback: Callable, consumer_running: callable):
        """Custom consumption loop with user-provided callback"""
        try:
            self.consumer.subscribe(topics)
            while self.running:
                msg = self.consumer.poll(timeout=0.2)
                if msg is None: 
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition event
                        sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                        (msg.topic(), msg.partition(), msg.offset()))
                    elif msg.error():
                        raise KafkaException(msg.error())
                else:
                    callback(msg)
        except Exception as e:
            print(f"Error in custom consume loop: {e}")
        finally:
            self.consumer.close()

    def shutdown(self):
        """Shutdown the consumer loop"""
        self.running = False