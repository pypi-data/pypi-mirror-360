
import serial.tools.list_ports
import json
import os
import logging

class COMPortFinder:  
    def __init__(self, config_path):  
        """
        Initialize the COMPortFinder.
        
        :param config_path: Path to configuration JSON file
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                self.device_ports = config_data.get('device_ports', {})
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            self.device_ports = {}
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in config file: {config_path}")
            self.device_ports = {}

    def get_ports_info(self, verbose=False):  
        """
        Retrieve detailed information about available COM ports.
        
        :param verbose: If True, print port details
        :return: List of port information dictionaries
        """
        ports_info = []  
        for port in serial.tools.list_ports.comports():  
            port_info = {  
                'device': port.device,  
                'name': port.name,  
                'description': port.description,  
                'hwid': port.hwid,  
                'vid': port.vid,  
                'pid': port.pid,  
                'manufacturer': port.manufacturer,  
                'location': port.location,  
                'serial_number': port.serial_number,  
            }  
            ports_info.append(port_info)  
            
            if verbose:  
                print(f"Device: {port_info['device']}\t"
                      f"VID: {port_info['vid']}\t"
                      f"PID: {port_info['pid']}")  
        return ports_info  
    
    def find_ports(self, *device_names):   
        """
        Find COM ports for specific device names.
        
        :param device_names: Names of devices to find
        :return: List of matching COM ports
        """
        ports = []  
        
        for device_name in device_names:  
            if device_name in self.device_ports:    
                target_vid, target_pid = self.device_ports[device_name]
                
                # Find ports matching the VID and PID
                matching_ports = [
                    port.device for port in serial.tools.list_ports.comports()
                    if port.vid == target_vid and port.pid == target_pid
                ]
                
                ports.extend(matching_ports)   
            else:  
                self.logger.warning(f"Device '{device_name}' not recognized.")  
        
        return ports
 
# if __name__ == "__main__":  
     
#     DEFAULT_CONFIG = {  
#         "device_ports": {  
#             "CheezUSB_VCP": [1155, 22336],  
#             "CheezBLE_VCP": [6790, 21971], 
#             "CheezBLE_VCP_V2": [6790, 29987]
#         },  
#         "default_baudrate": 115200,   
#         "BufferSize": 2000
#     }  
     
#     os.makedirs('config', exist_ok=True)   
#     config_path = 'config/config.json'  
#     with open(config_path, 'w', encoding='utf-8') as f:  
#         json.dump(DEFAULT_CONFIG, f, indent=4)  
#     port_finder = COMPortFinder(config_path)  
  
#     print("\n1. Retrieving All Available Ports:")  
#     all_ports = port_finder.get_ports_info(verbose=True)  

#     print("\n2. Finding Specific Device Ports:")   
#     USB_ports = port_finder.find_ports("CheezUSB_VCP")   
#     BLE2USB_ports = port_finder.find_ports("CheezBLE_VCP")   
#     BLE2USB_V2_ports = port_finder.find_ports("CheezBLE_VCP_V2")   

#     print("BLE2USB Ports:", USB_ports)  
#     print("BLE2USB Ports:", BLE2USB_ports)  
#     print("BLE2USB V2 Ports:", BLE2USB_V2_ports)   
 