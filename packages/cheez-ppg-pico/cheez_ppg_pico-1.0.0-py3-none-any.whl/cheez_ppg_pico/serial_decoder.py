import asyncio
import struct
import time
from aioserial import AioSerial

class SerialDecoder:
    def __init__(self, port, baud):
        """
        Initialize the SerialDecoder.
        
        :param port: COM port to connect
        :param baud: Baudrate for connection 
        """
        self.port = port
        self.baudrate = baud
        self.serial = AioSerial(port=self.port, baudrate=self.baudrate, timeout=None)
        self._reset_state()
    
    def _reset_state(self):
        self.times = 0
        self.buffer = bytearray()  # 用于存储接收的数据

        self.frame_count = 0  
        self.start_time = time.time()  
        self.last_frame_count = 0  
        self.packet_rate = 0  

        # 新协议的数据存储
        self.device_id = 0
        self.battery = 0
        self.data1 = 0
        self.data2 = 0
        self.data3 = 0
        self.data4 = 0
        self.data5 = 0
        self.data6 = 0
        self.data7 = 0
        self.data8 = 0
        self.data9 = 0
        self.data10 = 0
        self.data11 = 0
        self.data12 = 0
        self.data13 = 0

    async def read_data(self): 
        try:   
            # 读取直到遇到字节 b'\xcc\xcc'  
            data = await asyncio.wait_for(self.serial.read_until_async(b'\xcc\xcc'), timeout=100)  
            if data : 
                self.buffer.extend(data) 
                result = self._process_buffer()
                self._update_packet_rate() 
                return result
                
        except asyncio.TimeoutError:  
            print("read data Timeout")
            return None    
    
    def _process_buffer(self): 
        # 准备默认的数据字典
        Data = { 
            'time': self.frame_count, 
            'DeviceID': self.device_id,
            'Battery': self.battery,
            'PEAK': self.data1,
            'PPG': self.data2,
            'HR':self.data3,
            'HRV': self.data4,
            'accX': self.data5,
            'accY': self.data6,
            'accZ': self.data7,
            'gyroX': self.data8,
            'gyroY': self.data9,
            'gyroZ': self.data10,
            'Pitch': self.data11,
            'Roll': self.data12,
            'Yaw': self.data13
        }
         
        # 检查缓冲区是否有足够的数据（31字节完整帧）
        if len(self.buffer) >= 31:   
            if self.buffer[0] == 204 and self.buffer[1] == 204:  
                
                try:
                    # 解析帧: 设备ID(1B), 数据长度(1B), 电池(1B), 
                    # peak(1B), ppg(2B), hr(2B),hrv(2B), accX(2B), accY(2B), accZ(2B),
                    # gyroX(2B), gyroY(2B), gyroZ(2B), Pitch(2B), Roll(2B), Yaw(2B), checksum(1B)
                    device_id = self.buffer[2]
                    data_len = self.buffer[3]
                    battery_byte = self.buffer[4]
                    ppg_peak = self.buffer[5]
                    ppg_value = self.buffer[6:8]
                    hr_value = self.buffer[8:10]
                    hrv_value = self.buffer[10:12]
                    acc_x = self.buffer[12:14]
                    acc_y = self.buffer[14:16]
                    acc_z = self.buffer[16:18]
                    gyro_x = self.buffer[18:20]
                    gyro_y = self.buffer[20:22]
                    gyro_z = self.buffer[22:24]
                    pitch_value = self.buffer[24:26]
                    roll_value = self.buffer[26:28]
                    yaw_value = self.buffer[28:30]
                    checksum = self.buffer[30]

                    # 解析大端格式的数据
                    data1 = ppg_peak  # 直接使用peak值
                    data2, = struct.unpack('>h', ppg_value)
                    data3, = struct.unpack('>h', hr_value)
                    data4, = struct.unpack('>h', hrv_value)
                    data5, = struct.unpack('>h', acc_x)
                    data6, = struct.unpack('>h', acc_y)
                    data7, = struct.unpack('>h', acc_z)
                    data8, = struct.unpack('>h', gyro_x)
                    data9, = struct.unpack('>h', gyro_y)
                    data10, = struct.unpack('>h', gyro_z)
                    data11, = struct.unpack('>h', pitch_value)
                    data12, = struct.unpack('>h', roll_value)
                    data13, = struct.unpack('>h', yaw_value)

                    # 检查数据长度是否正确 
                    if data_len != 31:
                        print(f"[E]Length: {data_len}")
                        self.buffer = self.buffer[2:]  # 只移除帧头，继续寻找下一个帧
                        return Data

                    # 正确计算校验和：累加所有单独的字节
                    calculated_checksum = (
                        self.buffer[4] + self.buffer[5] + self.buffer[6] + self.buffer[7] +
                        self.buffer[8] + self.buffer[9] + self.buffer[10] + self.buffer[11] +
                        self.buffer[12] + self.buffer[13] + self.buffer[14] + self.buffer[15] +
                        self.buffer[16] + self.buffer[17] + self.buffer[18] + self.buffer[19] +
                        self.buffer[20] + self.buffer[21] + self.buffer[22] + self.buffer[23] +
                        self.buffer[24] + self.buffer[25] + self.buffer[26] + self.buffer[27] +
                        self.buffer[28] + self.buffer[29]
                    ) & 0xFF
                    
                    # 验证校验和
                    if calculated_checksum != checksum:
                        print(f"[E]Checksum: C:{calculated_checksum}, R:{checksum}")
                        self.buffer = self.buffer[2:]  # 只移除帧头，继续寻找下一个帧
                        return Data

                    # 更新类属性
                    self.device_id = device_id
                    self.battery = battery_byte
                    self.data1 = data1
                    self.data2 = data2
                    self.data3 = data3
                    self.data4 = data4
                    self.data5 = data5
                    self.data6 = data6
                    self.data7 = data7
                    self.data8 = data8
                    self.data9 = data9
                    self.data10 = data10
                    self.data11 = data11
                    self.data12 = data12
                    self.data13 = data13

                    # 增加帧计数
                    self.frame_count += 1

                    # 更新数据字典
                    Data = { 
                        'time': self.frame_count,
                        'DeviceID': device_id,
                        'Battery': battery_byte,
                        'PEAK': data1,
                        'PPG': data2,
                        'HR': data3,
                        'HRV': data4,
                        'accX': data5,
                        'accY': data6,
                        'accZ': data7,
                        'gyroX': data8,
                        'gyroY': data9,
                        'gyroZ': data10,
                        'Pitch': data11,
                        'Roll': data12,
                        'Yaw': data13
                    }

                    # 从缓冲区移除已处理的帧
                    self.buffer = self.buffer[31:]

                except Exception as e:
                    print(f"Error processing frame: {e}")
                    self.buffer = self.buffer[2:]  # 移除帧头，继续处理
            else:  
                # 丢弃无效的字节  
                self.buffer.pop(0)  # 移除缓冲区的第一个字节   
        return Data 

    def _update_packet_rate(self):  
        """Update the packet rate calculation."""
        current_time = time.time()  
        elapsed_time = current_time - self.start_time  
        
        if elapsed_time >= 1:  
            self.packet_rate = self.frame_count - self.last_frame_count  
            self.last_frame_count = self.frame_count  
            self.start_time = current_time   

    def get_packet_rate(self):        
        """
        Get the current packet rate.
        
        :return: Packets per second
        """
        return self.packet_rate 

    def close(self):
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()

    def open(self):
        """Open the serial connection."""
        if self.serial and not self.serial.is_open:
            self.serial.open()

    def is_open(self):
        """
        Check if the serial connection is open.
        
        :return: Connection status
        """
        return self.serial.is_open if self.serial else False

  