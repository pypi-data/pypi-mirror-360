import json
from confluent_kafka import Producer
from typing import Dict, Any, Callable


class AsyncProducer:
    """Asynchronous Kafka producer for sending messages"""
    
    def __init__(self, bootstrap_servers: str = '127.0.0.1:9092', client_id: str = 'replayservice'):
        """Initialize the Kafka producer with configuration"""
        self.conf = {
            'bootstrap.servers': bootstrap_servers,
            'client.id': client_id
        }
        self.producer = Producer(self.conf)
    
    def default_delivery_callback(self, err, msg):
        """Default callback for message delivery reports"""
        if err is not None:
            print(f"Failed to deliver message: {str(msg)}: {str(err)}")
        else:
            print(f"Message produced: {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
    
    def produce_message(self, topic: str, key: str, value: Dict[str, Any], callback: Callable = None) -> None:
        """Produce a message to a Kafka topic"""
        if callback is None:
            callback = self.default_delivery_callback
            
        try:
            # Convert value to JSON string
            value_str = json.dumps(value)
            
            # Produce message
            self.producer.produce(topic, key=key, value=value_str, callback=callback)
            
            # Poll to handle delivery reports
            self.producer.poll(0)
        except Exception as e:
            print(f"Error producing message: {e}")
    
    def flush(self, timeout: float = 1.0) -> int:
        """Flush the producer to ensure all messages are sent"""
        return self.producer.flush(timeout)