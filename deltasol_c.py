from resol_protocol import *

class PacketProcessor:
    def __init_(self):
        pass
    
class DeltaSolC(PacketProcessor):
    SRC_NAME = "RESOL DeltaSol C"
    SRC_ADDRESS = 0x4212
    PROTOCOL_VERSION = 0x10

    TEMP_S1 = {
        'offset': 0,
        'size': 2,
        'factor': 0.1,
        'suffix': '*C'
    }


    TEMP_S2 = {
        'offset': 2,
        'size': 2,
        'factor': 0.1,
        'suffix': '*C'
    }

    
    TEMP_S3 = {
        'offset': 4,
        'size': 2,
        'factor': 0.1,
        'suffix': '*C'
    }

    
    TEMP_S4 = {
        'offset': 6,
        'size': 2,
        'factor': 0.1,
        'suffix': '*C'
    }

    PUMP_SR1 = {
        'offset': 8,
        'size': 1,
        'factor': 1,
        'suffix': '%'
    }

    
    PUMP_SR2 = {
        'offset': 9,
        'size': 1,
        'factor': 1,
        'suffix': '%'
    }

    ERROR_MASK = {
        'offset': 10,
        'size': 1,
        'factor': None,
        'suffix': None
    }
    
    VARIANT = {
        'offset': 11,
        'size': 1,
        'factor': None,
        'suffix': None
    }

    HOURS_R1 = {
        'offset': 12,
        'size': 2,
        'factor': 1,
        'suffix': 'h'
    }

    HOURS_R2 = {
        'offset': 14,
        'size': 2,
        'factor': 1,
        'suffix': 'h'
    }
    
    HEAT_QTY_1 = {
        'offset': 16,
        'size': 2,
        'factor': 1,
        'suffix': 'Wh'
    }

    HEAT_QTY_1K = {
        'offset': 18,
        'size': 2,
        'factor': 10**3,
        'suffix': 'Wh'
    }

    HEAT_QTY_1M = {
        'offset': 20,
        'size': 2,
        'factor': 10**6,
        'suffix': 'Wh'
    }

    SYSTEM_TIME = {
        'offset': 22,
        'size': 2,
        'factor': 1,
        'suffix': None
    }


    def __init__(self):
        super(DeltaSolC, self).__init__()
