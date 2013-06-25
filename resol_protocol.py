class VBusProtocolException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

    
class VBusProtocol:
    version = None
    frame = None 

    @property
    def supported_versions(self):
        return [1, 2]
    
    def __init__(self, frame):
        if frame[0] == 0xAA:
            version = frame[5] / 0x10
            if version not in self.supported_versions:
                raise VBusProtocolException('Unsupported protocol version: %s' % version)
            self.version = version
            self.frame = frame
        else:
            raise VBusProcotolException('No SYNC byte found')
            
        
    def calculate_crc(self, offset, length):
        crc = 0x7F
	for i in range(0, length - 1):
            crc = (crc - self.frame[offset + i]) & 0x7F
	return crc

    def extract_septett(self, offset, length):
        septett = 0
	for i in range(0, length - 1):
            if self.frame[offset + i] == 0x80:
                self.frame[offset + i] &= 0x7F
		septett |= 1 << i
	self.frame[offset + length] = septett
	return septett

class VBusPacket(VBusProtocol):
    def __init__(self, frame):
        super(VBusPacket, self).__init__(frame)
      
    @property
    def checksum(self):
        if self.version == 1:
            offset = 1
            length = 8
        else:
            offset = 1
            length = 14
        return self.calculate_crc(offset, length)

    @property
    def command(self):
        return self.frame[7] << 4 + self.frame[6]
            
    @property
    def payload_frame_count(self):
        return self.frame[8]

    @property
    def source_address(self):
        return self.frame[4] << 4 + self.frame[3]

    @property
    def destination_address(self):
        return self.frame[2] << 4 + self.frame[1]


    def get_payload_value(self, value_spec):
        size = value_spec['size']
        offset = value_spec['offset']
        factor = value_spec['factor'] or 1
        
        if size == 1:
            value = self.frame[offset]
        elif size == 2:
            value = self.frame[offset + 1] << 4 + self.frame[offset]
        else:
            raise VBusProtocolException('Unsupported payload value size')
        return value * factor
