from .serial_decoder import SerialDecoder  
from .port_manager import COMPortFinder   
import os   
import json   

class CheezPico:  
    def __init__(self, config_path=None):  
        """  
        Initialize the Cheez SDK with optional custom config path.  
        
        :param config_path: Path to custom configuration file (optional)  
        """  
        # Define default config  
        default_config = {  
            "baud": 115200,  
            "device_ports": {  
                "CheezUSB_VCP": [1155, 22336],  
                "CheezBLE_VCP": [6790, 21971],  
                "CheezBLE_VCP_V2": [6790, 29987]  
            }  
        }  
        
        # Use default config path if not provided  
        if config_path is None:  
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.json')  
        
        # Check current directory for config.json  
        current_dir_config = os.path.join(os.getcwd(), 'config.json')  
        config = default_config.copy()  
        
        # Try to load from current directory first  
        if os.path.exists(current_dir_config):  
            try:  
                with open(current_dir_config, 'r') as f:  
                    existing_config = json.load(f)  
                    # Merge with default config  
                    config.update(existing_config)  
                    # Ensure device_ports are merged properly  
                    if "device_ports" in existing_config:  
                        config["device_ports"].update(existing_config["device_ports"])  
            except (json.JSONDecodeError, IOError):    
                pass  
        
        # Write or update config.json in current directory  
        try:  
            with open(current_dir_config, 'w') as f:  
                json.dump(config, f, indent=4)  
        except IOError:  
            print(f"Warning: Could not write to config file at {current_dir_config}")  
        
        # Ensure the config directory exists  
        config_dir = os.path.dirname(config_path)  
        if not os.path.exists(config_dir):  
            os.makedirs(config_dir, exist_ok=True)  
        
        # Use the merged/default config for the port manager  
        self.port_manager = COMPortFinder(current_dir_config)  
        self._serial_decoder = None  
        
    def list_ports(self, verbose=False):  
        """  
        List available COM ports.  
        
        :param verbose: If True, print detailed port information  
        :return: List of available ports  
        """  
        return self.port_manager.get_ports_info(verbose)  
    
    def find_devices(self, *device_names):  
        """  
        Find specific device ports.  
        
        :param device_names: Names of devices to find (e.g., 'CheezUSB_VCP', 'CheezBLE_VCP')  
        :return: List of matching COM ports  
        """  
        return self.port_manager.find_ports(*device_names)  
    
    def connect(self, port=None, baudrate=115200):  
        """  
        Connect to a serial device.  
        
        :param port: COM port to connect (auto-detect if None)  
        :param baudrate: Baudrate for connection  
        :return: SerialDecoder instance  
        """  
        # If no port specified, try to auto-detect  
        if port is None:  
            ports = self.find_devices("CheezUSB_VCP", "CheezBLE_VCP", "CheezBLE_VCP_V2")  
            if not ports:  
                raise ValueError("No compatible devices found")  
            port = ports[0]  
        
        self._serial_decoder = SerialDecoder(port, baudrate)  
        return self._serial_decoder  
    
    def disconnect(self):  
        """  
        Disconnect the current serial connection.  
        """  
        if self._serial_decoder:  
            self._serial_decoder.close()  
            self._serial_decoder = None  
            
    async def set_device_id(self, device_id):  
        """  
        Set the device ID.  
        
        :param device_id: ID value between 0-255  
        :return: True if successful, False otherwise  
        :raises: ValueError if not connected  
        """  
        if not self._serial_decoder:  
            raise ValueError("Not connected to any device")  
        return await self._serial_decoder.set_device_id(device_id)  
    
    async def set_sampling_rate(self, rate="250 Hz"):  
        """  
        Set the sampling rate.  
        
        :param rate: Sampling rate ("100 Hz", "250 Hz", or "500 Hz")  
        :return: True if successful, False otherwise  
        :raises: ValueError if not connected  
        """  
        if not self._serial_decoder:  
            raise ValueError("Not connected to any device")  
        return await self._serial_decoder.set_sampling_rate(rate)  
    
    async def set_filter_state(self, enable=True):  
        """  
        Enable or disable filtering.  
        
        :param enable: True to enable filtering, False to disable  
        :return: True if successful, False otherwise  
        :raises: ValueError if not connected  
        """  
        if not self._serial_decoder:  
            raise ValueError("Not connected to any device")  
        return await self._serial_decoder.set_filter_state(enable)  
    
    async def set_wear_detection(self, enable=True):  
        """  
        Enable or disable wear detection.  
        
        :param enable: True to enable wear detection, False to disable  
        :return: True if successful, False otherwise  
        :raises: ValueError if not connected  
        """  
        if not self._serial_decoder:  
            raise ValueError("Not connected to any device")  
        return await self._serial_decoder.set_wear_detection(enable)  
     

