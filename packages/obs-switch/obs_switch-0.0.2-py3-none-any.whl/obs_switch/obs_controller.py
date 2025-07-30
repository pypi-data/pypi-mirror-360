import websocket
import json
import base64
import hashlib
import threading
import time
from typing import Dict, Callable

class OBSController:
    """Controller for OBS Studio via WebSocket"""
    
    # WebSocket operation codes
    OP_HELLO = 0
    OP_IDENTIFY = 1
    OP_IDENTIFIED = 2
    OP_REIDENTIFY = 3
    OP_EVENT = 5
    OP_REQUEST = 6
    OP_REQUEST_RESPONSE = 7
    OP_REQUEST_BATCH = 8
    OP_REQUEST_BATCH_RESPONSE = 9
    
    def __init__(self):
        # Connection properties
        self.host = None
        self.port = None
        self.password = None
        self.ws = None
        self.connected = False
        self.reconnect_thread = None
        self.should_reconnect = False
        
        # OBS state
        self.scenes = []
        self.current_scene = None
        self.recording = False
        
        # Message tracking
        self.message_id_counter = 0
        self.response_callbacks = {}
        self.event_callbacks = {}
    
    def get_message_id(self) -> str:
        """Generate a unique message ID"""
        self.message_id_counter += 1
        return f"m{self.message_id_counter}"
    
    def connect(self, host: str = "localhost", port: int = 4455, password: str = ""):
        """Connect to OBS WebSocket"""
        self.host = host
        self.port = port
        self.password = password
        
        # Create WebSocket connection
        ws_url = f"ws://{host}:{port}"
        
        try:
            # Close existing connection if any
            if self.ws:
                self.ws.close()
            
            # Create new connection
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_open=lambda ws: self._on_open(ws),
                on_message=lambda ws, msg: self._on_message(ws, msg),
                on_error=lambda ws, error: self._on_error(ws, error),
                on_close=lambda ws, close_status_code, close_msg: self._on_close(ws, close_status_code, close_msg)
            )
            
            # Start WebSocket connection in a thread
            threading.Thread(target=self.ws.run_forever, daemon=True).start()
            return True
        except Exception as e:
            print(f"Error connecting to OBS WebSocket: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from OBS WebSocket"""
        self.should_reconnect = False
        if self.ws:
            self.ws.close()
            self.ws = None
        self.connected = False
        
        # Trigger connection status event
        self._trigger_event("connection_status", {"connected": False})
    
    def _on_open(self, ws):
        """WebSocket connection opened"""
        print("WebSocket connection opened")
    
    def _on_message(self, ws, message):
        """WebSocket message received"""
        try:
            data = json.loads(message)
            op_code = data.get('op')
            
            if op_code == self.OP_HELLO:
                self._handle_hello(data)
            elif op_code == self.OP_IDENTIFIED:
                self._handle_identified(data)
            elif op_code == self.OP_EVENT:
                self._handle_event(data)
            elif op_code == self.OP_REQUEST_RESPONSE:
                self._handle_request_response(data)
        except Exception as e:
            print(f"Error handling WebSocket message: {e}")
    
    def _on_error(self, ws, error):
        """WebSocket error occurred"""
        print(f"WebSocket error: {error}")
        self.connected = False
        
        # Trigger connection status event
        self._trigger_event("connection_status", {"connected": False})
        
        # Attempt to reconnect if enabled
        if self.should_reconnect and not self.reconnect_thread:
            self.reconnect_thread = threading.Thread(target=self._reconnect)
            self.reconnect_thread.daemon = True
            self.reconnect_thread.start()
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket connection closed"""
        print(f"WebSocket closed: {close_status_code} - {close_msg}")
        self.connected = False
        
        # Trigger connection status event
        self._trigger_event("connection_status", {"connected": False})
        
        # Attempt to reconnect if enabled
        if self.should_reconnect and not self.reconnect_thread:
            self.reconnect_thread = threading.Thread(target=self._reconnect)
            self.reconnect_thread.daemon = True
            self.reconnect_thread.start()
    
    def _reconnect(self):
        """Attempt to reconnect to OBS WebSocket"""
        retry_count = 0
        max_retries = 10
        retry_delay = 2
        
        while self.should_reconnect and retry_count < max_retries:
            print(f"Attempting to reconnect to OBS WebSocket ({retry_count + 1}/{max_retries})...")
            if self.connect(self.host, self.port, self.password):
                print("Reconnected to OBS WebSocket")
                break
            
            retry_count += 1
            time.sleep(retry_delay)
        
        self.reconnect_thread = None
    
    def _handle_hello(self, data):
        """Handle Hello message from OBS WebSocket"""
        d = data.get('d', {})
        authentication = d.get('authentication')
        
        # Prepare identify message
        identify = {
            'op': self.OP_IDENTIFY,
            'd': {
                'rpcVersion': 1
            }
        }
        
        # Add authentication if required
        if authentication:
            challenge = authentication.get('challenge')
            salt = authentication.get('salt')
            
            # Generate authentication response
            secret = base64.b64encode(
                hashlib.sha256(
                    hashlib.sha256((self.password + salt).encode()).digest() + 
                    challenge.encode()
                ).digest()
            ).decode()
            
            identify['d']['authentication'] = secret
        
        # Send identify message
        self.ws.send(json.dumps(identify))
    
    def _handle_identified(self, data):
        """Handle Identified message from OBS WebSocket"""
        self.connected = True
        print("Successfully identified with OBS WebSocket")
        
        # Trigger connection status event
        self._trigger_event("connection_status", {"connected": True})
        
        # Get initial scene list
        self.get_scene_list()
        
        # Get initial recording status
        self.get_recording_status()
    
    def _handle_event(self, data):
        """Handle Event message from OBS WebSocket"""
        d = data.get('d', {})
        event_type = d.get('eventType')
        event_data = d.get('eventData', {})
        
        if event_type == 'CurrentProgramSceneChanged':
            # Update current scene
            self.current_scene = event_data.get('sceneName')
            
            # Trigger scene changed event
            self._trigger_event("scene_changed", {
                "scene": self.current_scene
            })
        
        elif event_type == 'SceneListChanged':
            # Update scenes list
            self.get_scene_list()
        
        elif event_type == 'RecordStateChanged':
            # Update recording status
            self.recording = event_data.get('outputActive', False)
            
            # Trigger recording status event
            self._trigger_event("recording_status", {
                "recording": self.recording,
                "state": event_data.get('outputState')
            })
        
        # Forward all events
        self._trigger_event("obs_event", {
            "type": event_type,
            "data": d.get('eventData', {})
        })
    
    def _handle_request_response(self, data):
        """Handle Request Response message from OBS WebSocket"""
        d = data.get('d', {})
        request_type = d.get('requestType')
        request_id = d.get('requestId')
        
        # Check for successful response
        status = d.get('requestStatus', {})
        success = status.get('result', False) is True
        
        if not success:
            error_message = status.get('comment', 'Unknown error')
            print(f"Request {request_type} failed: {error_message}")
        
        response_data = d.get('responseData', {})
        
        if request_type == 'GetSceneList':
            # Update scenes list
            self.scenes = response_data.get('scenes', [])
            self.current_scene = response_data.get('currentProgramSceneName')
            
            # Trigger scene list event
            self._trigger_event("scene_list", {
                "scenes": self.scenes,
                "current": self.current_scene
            })
        
        elif request_type == 'GetRecordStatus':
            # Update recording status
            self.recording = response_data.get('outputActive', False)
            
            # Trigger recording status event
            self._trigger_event("recording_status", {
                "recording": self.recording,
                "state": response_data.get('outputState')
            })
        
        elif request_type == 'GetSourceScreenshot':
            # Trigger screenshot event
            self._trigger_event("screenshot_data", {
                "imageData": response_data.get('imageData', '')
            })
        
        # Call response callback if registered
        if request_id in self.response_callbacks:
            callback = self.response_callbacks.pop(request_id)
            callback(success, response_data, error_message if not success else None)
    
    def send_request(self, request_type: str, data: Dict = None, callback: Callable = None) -> bool:
        """Send request to OBS WebSocket"""
        if not self.connected or not self.ws:
            return False
        
        request_id = self.get_message_id()
        
        request = {
            'op': self.OP_REQUEST,
            'd': {
                'requestType': request_type,
                'requestId': request_id
            }
        }
        
        if data:
            request['d']['requestData'] = data
        
        # Register callback if provided
        if callback:
            self.response_callbacks[request_id] = callback
        
        try:
            self.ws.send(json.dumps(request))
            return True
        except Exception as e:
            print(f"Error sending request to OBS: {e}")
            return False
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """Register a callback for a specific event type"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        
        self.event_callbacks[event_type].append(callback)
    
    def _trigger_event(self, event_type: str, data: Dict):
        """Trigger registered callbacks for an event"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event callback for {event_type}: {e}")
    
    # --- OBS Control Methods ---
    
    def get_scene_list(self, callback: Callable = None) -> bool:
        """Get list of scenes from OBS"""
        return self.send_request('GetSceneList', callback=callback)
    
    def change_scene(self, scene_name: str, callback: Callable = None) -> bool:
        """Change current scene in OBS"""
        return self.send_request('SetCurrentProgramScene', {
            'sceneName': scene_name
        }, callback=callback)
    
    def start_recording(self, callback: Callable = None) -> bool:
        """Start recording in OBS"""
        return self.send_request('StartRecord', callback=callback)
    
    def stop_recording(self, callback: Callable = None) -> bool:
        """Stop recording in OBS"""
        return self.send_request('StopRecord', callback=callback)
    
    def get_recording_status(self, callback: Callable = None) -> bool:
        """Get recording status from OBS"""
        return self.send_request('GetRecordStatus', callback=callback)
    
    def toggle_recording(self, callback: Callable = None) -> bool:
        """Toggle recording state in OBS"""
        if self.recording:
            return self.stop_recording(callback)
        else:
            return self.start_recording(callback)
    
    def get_screenshot(self, source_name: str = None, width: int = 1280, 
                      height: int = 720, image_format: str = 'png',
                      callback: Callable = None) -> bool:
        """Get a screenshot from OBS"""
        data = {}
        
        # If source name is provided, use it
        if source_name:
            data['sourceName'] = source_name
        
        # Set image dimensions and format
        data['imageWidth'] = width
        data['imageHeight'] = height
        data['imageFormat'] = image_format
        
        return self.send_request('GetSourceScreenshot', data, callback=callback)