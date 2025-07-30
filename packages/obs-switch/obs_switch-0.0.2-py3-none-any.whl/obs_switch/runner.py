import sys
import json
import threading
import time
from typing import List, Dict, Any, Callable

# Import our modules
from obs_controller import OBSController
from switch_controller import SwitchController
from async_consumer import AsyncConsumer
from switch_handler import translate_code_to_macros


class Runner:
    """
    Main runner class that coordinates between OBS and Switch controllers
    based on Kafka events.
    """
    
    def __init__(self):
        # Initialize controllers
        self.obs = OBSController()
        self.switch = SwitchController()
        
        # Kafka consumer
        self.consumer = None
        self.consumer_running = True
        self.consumer_thread = None
        
        # Register event handlers
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """
        Register event handlers for OBS and Switch controllers
        """
        # OBS event handlers
        self.obs.register_event_callback("connection_status", self._on_obs_connection_status)
        self.obs.register_event_callback("scene_changed", self._on_scene_changed)
        self.obs.register_event_callback("recording_status", self._on_recording_state_changed)
        
        # Switch controller event handlers
        self.switch.register_event_callback("connection_status", self._on_switch_connection_status)
        self.switch.register_event_callback("controller_created", self._on_create_controller)
        self.switch.register_event_callback("error", self._on_switch_error)
    
    def _on_obs_connection_status(self, data):
        """
        Handle OBS connection status changes
        """
        if data['connected']:
            print("Connected to OBS WebSocket server")
        else:
            print("Disconnected from OBS WebSocket server")
            if 'error' in data:
                print(f"Error: {data['error']}")
    
    def _on_scene_changed(self, data):
        """
        Handle OBS scene changes
        """
        print(f"Scene changed to: {data['scene']}")
    
    def _on_recording_state_changed(self, data):
        """
        Handle OBS recording state changes
        """
        state = "Recording" if data['recording'] else "Stopped"
        print(f"Recording state changed: {state}")
    
    def _on_switch_connection_status(self, data):
        """
        Handle Switch controller connection status changes
        """
        if data.get('connected', False):
            print("Connected to the NXBT webapp.")
        else:
            print("Disconnected from the NXBT webapp.")
    
    def _on_create_controller(self, data):
        """
        Handle controller creation confirmation
        """
        index = data.get('index')
        print(f"Controller created with index: {index}")
    
    def _on_switch_error(self, data):
        """
        Handle Switch controller errors
        """
        message = data.get('message', 'Unknown error')
        print(f"Switch controller error: {message}")
    
    def _process_kafka_message(self, message):
        """
        Process incoming Kafka messages and trigger appropriate actions
        """
        try:
            key = message.key().decode('utf-8')
            value = json.loads(message.value())
            
            print(f"Received Kafka message - Key: {key}")
            print(f"Message content: {value}")
            
            # Process message based on event_type
            event_type = value.get('event_type')
            
            if event_type == 'obs_scene_change':
                # Change OBS scene
                scene_name = value.get('scene_name')
                if scene_name:
                    print(f"Changing OBS scene to: {scene_name}")
                    self.obs.change_scene(scene_name)
            
            elif event_type == 'obs_recording':
                # Control OBS recording
                action = value.get('action')
                if action == 'start':
                    print("Starting OBS recording")
                    self.obs.start_recording()
                elif action == 'stop':
                    print("Stopping OBS recording")
                    self.obs.stop_recording()
                elif action == 'toggle':
                    print("Toggling OBS recording")
                    self.obs.toggle_recording()
            
            elif event_type == 'switch_button':
                # Press Switch controller buttons
                buttons = value.get('buttons', [])
                delay = value.get('delay', 0.1)
                if buttons and self.switch.is_connected():
                    print(f"Pressing buttons: {buttons}")
                    self.switch.press_buttons(buttons, delay)
            
            elif event_type == 'switch_stick':
                # Move Switch controller stick
                stick = value.get('stick')
                x_value = value.get('x_value', 0)
                y_value = value.get('y_value', 0)
                delay = value.get('delay', 0.1)
                if stick and self.switch.is_connected():
                    print(f"Moving {stick} to ({x_value}, {y_value})")
                    self.switch.tilt_stick(stick, x_value, y_value, delay)
            
            elif event_type == 'switch_replay_code':
                # Enter replay code using Switch controller
                code = value.get('code')
                if code and self.switch.is_connected():
                    print(f"Entering replay code: {code}")
                    self._enter_replay_code(code)
        
        except Exception as e:
            print(f"Error processing Kafka message: {e}")
    
    def _enter_replay_code(self, code: str):
        """
        Enter a replay code using the Switch controller
        """
        try:
            # Translate the code to controller macros
            macro_sequences = translate_code_to_macros(code)
            
            # Execute each macro sequence
            for sequence in macro_sequences:
                if sequence:
                    # Convert macro sequence to button presses
                    for button in sequence:
                        if button:
                            # Map the macro to the actual button name
                            # This is a simplified approach - in reality you might need more complex mapping
                            self.switch.press_buttons([button], 0.1)
                            time.sleep(0.2)  # Add delay between button presses
                    
                    time.sleep(0.5)  # Add delay between sequences
        
        except Exception as e:
            print(f"Error entering replay code: {e}")
    
    def start_kafka_consumer(self, topics: List[str] = ['spl_replay_service'], bootstrap_servers: str = 'localhost:9092'):
        """
        Start the Kafka consumer in a separate thread
        """
        # Initialize Kafka consumer if not already initialized
        if self.consumer is None:
            conf = {
                'bootstrap.servers': bootstrap_servers,
                'group.id': 'obs_switch_consumer'
            }
            print(f"Initializing Kafka consumer with configuration: {conf}")
            self.consumer = AsyncConsumer(
                bootstrap_servers=conf['bootstrap.servers'],
                group_id=conf['group.id']
            )
        print(f"Starting Kafka consumer for topics: {topics}")
        self.consumer_running = True
        print(f"Consumer running: {self.consumer_running}")
        self.consumer_thread = threading.Thread(
            target=self.consumer.custom_consumer_loop,
            args=(topics, self._process_kafka_message, lambda: self.consumer_running)
        )
        print(f"Consumer thread: {self.consumer_thread}")
        self.consumer_thread.daemon = True
        self.consumer_thread.start()
        print(f"Started Kafka consumer for topics: {topics}")
    
    def stop_kafka_consumer(self):
        """
        Stop the Kafka consumer
        """
        self.consumer_running = False
        if self.consumer_thread:
            self.consumer_thread.join(timeout=5)
            print("Stopped Kafka consumer")
    
    def connect_obs(self, host: str = "localhost", port: int = 4455, password: str = None):
        """
        Connect to OBS WebSocket server
        """
        print(f"Connecting to OBS WebSocket at {host}:{port}...")
        return self.obs.connect(host, port, password)
    
    def connect_switch(self, url: str = "http://localhost:8000"):
        """
        Connect to NXBT webapp
        """
        try:
            print(f"Connecting to NXBT webapp at {url}...")
            return self.switch.connect(url)
        except Exception as e:
            print(f"Failed to connect to NXBT webapp: {e}")
            return False
    
    def disconnect(self):
        """
        Disconnect from all services
        """
        # Stop Kafka consumer
        self.stop_kafka_consumer()
        
        # Disconnect from OBS
        self.obs.disconnect()
        
        # Disconnect from Switch controller
        self.switch.disconnect()
    
    def run(self, 
            obs_host: str = "localhost", 
            obs_port: int = 4455, 
            obs_password: str = None,
            switch_url: str = "http://localhost:8000",
            kafka_bootstrap_servers: str = "localhost:9092",
            kafka_topics: List[str] = ['spl_replay_service']):
        """
        Run the main application
        """
        try:
            # Connect to OBS
            self.connect_obs(obs_host, obs_port, obs_password)
            
            # Connect to Switch controller
            self.connect_switch(switch_url)
            
            # Start Kafka consumer
            self.start_kafka_consumer(kafka_topics, kafka_bootstrap_servers)
            
            print("Runner is now active and listening for events...")
            print("Press Ctrl+C to exit")
            
            # Keep the main thread running
            while True:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nExiting...")
        
        finally:
            # Clean up resources
            self.disconnect()