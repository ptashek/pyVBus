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
from VBusProtocolException import VBusProtocolException

class VBusProtocol(object):
    version = None
    packet = None 
    
    HEADER_LEN = (10, 8)
    
    __commands = { 
        0x0100: 'Answer from module with requested value',
        0x0200: 'Write value, acknowledgement required',
        0x0300: 'Read value, acknowledgement required',
        0x0400: 'Write value, acknowledgement required',
        0x0500: 'VBus clearance by master module',
        0x0600: 'VBus clearance by slave module',
    }
    
    @property
    def supported_versions(self):
        return [1, 2]
    
    def __init__(self, packet):
        self.packet = list(packet)
    
        if not self.packet[0] == 0xAA:
            raise VBusProtocolException('No SYNC byte found')
                   
        self.version = self.packet[5] / 0x10           
        if self.version not in self.supported_versions:
            raise VBusProtocolException('Unsupported protocol version: %s' % self.version)
    
        if self.version == 1:   
            offset = 1
            length = 8
        elif self.version == 2:
            offset = 1
            length = 14
            
        if not self.packet[offset + length] == self.calculate_crc(offset, length):
            raise VBusProtocolException("Frame header checksum mismatch")         
                
    def calculate_crc(self, offset, length):
        crc = 0x7F
        for i in range(length):
            crc = (crc - self.packet[offset + i]) & 0x7F
        return crc

    def extract_septett(self, offset, length):
        septett = 0
        for i in range(length):
            if self.packet[offset + i] == 0x80:
                self.packet[offset + i] &= 0x7F
                septett |= 1 << i
        self.packet[offset + length] = septett
        return septett
    
    def inject_septett(self, offset, length):
        septett = self.packet[offset + length]
        index = 0
        
        for i in range(length):
            if not septett & (1 << i) == 0:
                index = offset + i
                self.packet[index] |= 0x80 
        
    def command_string(self, command_code):
        try:
            command_str = self.__commands[command_code]
        except KeyError:
            command_str = None 
        return command_str
