import time
from obs_switch.async_producer import AsyncProducer

# Main function with example messages
def main():
    # Kafka producer configuration
    conf = {
        'bootstrap.servers': '127.0.0.1:9092',
        'client.id': 'example_producer'
    }

    # Create producer instance
    producer = AsyncProducer(
        bootstrap_servers=conf['bootstrap.servers'],
        client_id=conf['client.id']
    )
    topic = 'spl_replay_service'
    
    # Example 1: Change OBS scene
    print("\nExample 1: Changing OBS scene to 'Game Capture'")
    producer.produce_message(
        topic=topic,
        key='obs_control',
        value={
            'event_type': 'obs_scene_change',
            'scene_name': 'Game Capture'
        }
    )
    time.sleep(1)  # Wait for action to complete
    
    # Example 2: Start recording in OBS
    print("\nExample 2: Starting OBS recording")
    producer.produce_message(
        topic=topic,
        key='obs_control',
        value={
            'event_type': 'obs_recording',
            'action': 'start'
        }
    )
    time.sleep(3)  # Wait for recording to start
    
    # Example 3: Press buttons on Switch controller
    print("\nExample 3: Pressing A button on Switch controller")
    producer.produce_message(
        topic=topic,
        key='switch_control',
        value={
            'event_type': 'switch_button',
            'buttons': ['A'],
            'delay': 0.2
        }
    )
    time.sleep(1)  # Wait for action to complete
    
    # Example 4: Move left stick on Switch controller
    print("\nExample 4: Moving left stick right on Switch controller")
    producer.produce_message(
        topic=topic,
        key='switch_control',
        value={
            'event_type': 'switch_stick',
            'stick': 'L_STICK',
            'x_value': 100,
            'y_value': 0,
            'delay': 0.5
        }
    )
    time.sleep(1)  # Wait for action to complete
    
    # Example 5: Enter a replay code
    print("\nExample 5: Entering replay code")
    producer.produce_message(
        topic=topic,
        key='switch_control',
        value={
            'event_type': 'switch_replay_code',
            'code': '1234-5678-9012'
        }
    )
    time.sleep(5)  # Wait for code entry to complete
    
    # Example 6: Stop recording in OBS
    print("\nExample 6: Stopping OBS recording")
    producer.produce_message(
        topic=topic,
        key='obs_control',
        value={
            'event_type': 'obs_recording',
            'action': 'stop'
        }
    )
    
    # Flush the producer to ensure all messages are sent
    producer.flush()
    print("\nAll example messages sent!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")