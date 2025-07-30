import json
import time

import socketio


class SwitchController:
    """Controller for Nintendo Switch via NXBT webapp"""

    def __init__(self):
        # Initialize socketio client
        self.sio = socketio.Client()
        self.controller_index = None
        self.connected = False

        # Register event handlers
        self.sio.on('connect', self._on_connect)
        self.sio.on('disconnect', self._on_disconnect)
        self.sio.on('create_pro_controller', self._on_create_controller)
        self.sio.on('error', self._on_error)

        # Initialize input packet template
        self.input_packet = {
            "L_STICK": {"PRESSED": False, "X_VALUE": 0, "Y_VALUE": 0},
            "R_STICK": {"PRESSED": False, "X_VALUE": 0, "Y_VALUE": 0},
            "DPAD_UP": False, "DPAD_LEFT": False, "DPAD_RIGHT": False, "DPAD_DOWN": False,
            "L": False, "ZL": False, "R": False, "ZR": False,
            "JCL_SR": False, "JCL_SL": False, "JCR_SR": False, "JCR_SL": False,
            "PLUS": False, "MINUS": False, "HOME": False, "CAPTURE": False,
            "Y": False, "X": False, "B": False, "A": False
        }

        # Event callbacks
        self.event_callbacks = {}

    # --- Connection Methods ---

    def connect(self, url: str = 'http://localhost:8000'):
        """Connect to the NXBT webapp"""
        try:
            self.sio.connect(url)
            return True
        except socketio.exceptions.ConnectionError as e:
            print(f"Failed to connect to the NXBT webapp {url}: {e}")
            return False

    def disconnect(self):
        """Disconnect from the NXBT webapp"""
        if self.sio.connected:
            self.sio.disconnect()
        self.connected = False
        self.controller_index = None

        # Trigger connection status event
        self._trigger_event("connection_status", {"connected": False})

    # --- Event Handlers ---

    def _on_connect(self):
        """Handle connection to the NXBT webapp"""
        print("Connected to the NXBT webapp.")
        self.connected = True

        # Request to create a controller
        self.sio.emit('web_create_pro_controller')

        # Trigger connection status event
        self._trigger_event("connection_status", {"connected": True})

    def _on_disconnect(self):
        """Handle disconnection from the NXBT webapp"""
        print("Disconnected from the NXBT webapp.")
        self.connected = False
        self.controller_index = None

        # Trigger connection status event
        self._trigger_event("connection_status", {"connected": False})

    def _on_create_controller(self, index):
        """Handle controller creation confirmation"""
        self.controller_index = index
        print(f"Controller created with index: {index}")

        # Trigger controller created event
        self._trigger_event("controller_created", {"index": index})

    def _on_error(self, message):
        """Handle error messages from the NXBT webapp"""
        print(f"An error occurred: {message}")

        # Trigger error event
        self._trigger_event("error", {"message": message})

    # --- Input Methods ---

    def send_input_state(self):
        """Send the current input packet to the server"""
        if self.controller_index is not None:
            self.sio.emit('input', json.dumps([self.controller_index, self.input_packet]))
            return True
        else:
            print("Waiting for controller to be created...")
            return False

    def press_and_release(self, buttons, delay=0.1):
        """Press and release a set of buttons"""
        if not isinstance(buttons, list):
            buttons = [buttons]

        # Press buttons
        for button in buttons:
            self.input_packet[button] = True
        self.send_input_state()

        # Wait for specified delay
        time.sleep(delay)

        # Release buttons
        for button in buttons:
            self.input_packet[button] = False
        self.send_input_state()

        return True

    def tilt_stick(self, stick, x, y, delay=0.1):
        """Tilt an analog stick to a specific position for a duration"""
        # Set stick position
        self.input_packet[stick]['X_VALUE'] = x
        self.input_packet[stick]['Y_VALUE'] = y
        self.send_input_state()

        # Wait for specified delay
        time.sleep(delay)

        # Reset stick position
        self.input_packet[stick]['X_VALUE'] = 0
        self.input_packet[stick]['Y_VALUE'] = 0
        self.send_input_state()

        return True

    # --- Event Callback System ---

    def register_event_callback(self, event_type: str, callback):
        """Register a callback for a specific event type"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []

        self.event_callbacks[event_type].append(callback)

    def _trigger_event(self, event_type: str, data: dict):
        """Trigger registered callbacks for an event"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in event callback for {event_type}: {e}")

    def is_connected(self) -> bool:
        return self.connected
