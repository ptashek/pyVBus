'''
   Copyright 2013 Lukasz Szmit

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
from VBusProtocol import VBusProtocol
from struct import unpack
from VBusProtocolException import VBusProtocolException
import time

class VBusPacket(VBusProtocol):
           
    header = {
      'dst_address': {
        'size': 2,
        'offset': 1
      },
      'src_address': {
        'size': 2,
        'offset': 3
      },
      'command': {
        'size': 2,
        'offset': 6
      },
      'payload_size': {
        'size': 1,
        'offset': 8
      },
      'checksum': {
        'size': 1,
        'offset': 9
      }
    }
    
    def __init__(self, packet):
        super(VBusPacket, self).__init__(packet)
        self.__timestamp = time.time()
        self.__size = len(packet)
        self.__src = self.get_value(self.header['src_address'])
        self.__dst = self.get_value(self.header['dst_address'])
        self.__cmd = self.get_value(self.header['command'])
        
        for data_byte in self.packet[1:]:
            if data_byte & 0x80 > 0x7F:
                raise VBusProtocolException("Byte (%s) has its MSB set: %s" % (data_byte, data_byte & 0x80 > 0x7))
         
        header_size = VBusProtocol.HEADER_LEN[self.version - 1]
        
        if self.version == 1:
            self.__pc = self.packet[8]
            self.__ps = self.__pc * 4
            if self.__size < header_size + self.__ps:
                raise VBusProtocolException("Packet too short. Expected %s bytes, got %s" % (header_size + self.__ps, self.__size))
            
            for i in range(self.__pc):
                s_index = header_size + 6 * i
                d_index = i * 4
                
                frame_crc = self.calculate_crc(s_index, 5)
                crc_byte = self.packet[s_index + 5]
                
                if not frame_crc == crc_byte:
                    raise VBusProtocolException("Data frame checksum invalid")
                
                self.inject_septett(s_index, 4)
                
                for j in range(4):
                    self.packet[d_index + j] = self.packet[s_index + j]
        else:
            self.__pc = 1
            self.__ps = self.__pc * 6
            if self.__size < header_size + self.__ps:
                raise VBusProtocolException("Packet too short. Expected %s bytes, got %s" % (header_size + self.__ps, self.__size))
            
            for i in range(self.__pc):
                s_index = header_size + 8 * i
                d_index = i * 6
                
                self.inject_septett(s_index, 6)
                
                for j in range(6):
                    self.packet[d_index + j] = self.packet[s_index + j]
                    
    @staticmethod
    def from_buffer(byte_buffer):
        packet_bytes = unpack('<' + 'B' * len(byte_buffer), byte_buffer)
        return VBusPacket(packet_bytes)
      
    def get_header_crc(self):
        if self.version == 1:
            offset = 1
            length = 8
        else:
            offset = 1
            length = 14
        return self.calculate_crc(offset, length)

    @property
    def command(self):
        return self.__cmd
            
    @property
    def payload_size(self):
        return self.__ps
    
    @property
    def source_address(self):
        return self.__src

    @property
    def destination_address(self):
        return self.__dst
    
    def get_value(self, value_spec):
        offset = value_spec['offset']
        size = value_spec['size']
        bit_size = size * 8
        value = 0
      
        try:
            factor = value_spec['factor']
        except KeyError:
            factor = None
       
        for i in range(size):
            if offset + i < self.__size:
                value += self.packet[(offset + i)] << (8 * i)
                       
        mask = (1 << bit_size) - 1
        sign_mask = 1 << bit_size
   
        if ((bit_size >= 7) and ((bit_size & 0x1) != 0) and ((value & sign_mask) != 0)):
            value |= mask ^ 0xFFFFFFFF
        else:
            value &= mask
            
        if factor:
            value *= factor
        return value   
    
    def __str__(self):
        return "Version: %s;  Destination: %s;  Source: %s; Command: '%s'" % (self.version, self.__dst, self.__src, self.command_string(self.__cmd))
