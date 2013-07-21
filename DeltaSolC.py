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
from PacketProcessor import PacketProcessor
from multiprocessing import cpu_count
from threading import current_thread
from VBusPacket import VBusPacket


class DeltaSolC(PacketProcessor):
    NAME = "RESOL DeltaSol C"
    # sensors: 4, relays: 2, module: 1, bus subaddress: 2
    ADDRESS = 16914  # 0x4212
    PROTOCOL_VERSION = 1  # 0x10

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
        'factor': 10 ** 3,
        'suffix': 'Wh'
    }

    HEAT_QTY_1M = {
        'offset': 20,
        'size': 2,
        'factor': 10 ** 6,
        'suffix': 'Wh'
    }

    SYSTEM_TIME = {
        'offset': 22,
        'size': 2,
        'factor': 1,
        'suffix': None
    }
    
    def __init__(self, results_callback=None):
        num_workers = cpu_count()
	if results_callback is None:
            results_callback = self.show
	super(DeltaSolC, self).__init__(num_workers, results_callback)
        
    def show(self):
        while True:
            result = self.result_q.get()
            if result is None:
                break
            print result
        
    def process(self):
        while True:
            try: 
                byte_buffer = self.work_q.get()
                    
                if byte_buffer is None:
                    break
                    
                packet = VBusPacket.from_buffer(byte_buffer)
               
                if packet.version == DeltaSolC.PROTOCOL_VERSION and packet.source_address == self.ADDRESS:
                    ts1 = packet.get_value(self.TEMP_S1)
                    ts2 = packet.get_value(self.TEMP_S2)
                    ts3 = packet.get_value(self.TEMP_S3)
                    ts4 = packet.get_value(self.TEMP_S4)
                    p_sr1 = packet.get_value(self.PUMP_SR1)
                    p_sr2 = packet.get_value(self.PUMP_SR2)
                    h_r1 = packet.get_value(self.HOURS_R1)
                    h_r2 = packet.get_value(self.HOURS_R2)
                    sys_t = packet.get_raw_bytes(self.SYSTEM_TIME)
                    self.result_q.put({"t1":ts1, "t2":ts2, "t3":ts3, "t4":ts4, "sr1":p_sr1, "sr2":p_sr2, "h1":h_r1, "h2":h_r2, "sys_t":sys_t})
                else:
                    packet = None
            except Exception as e:
                print "Exception on %s: %s" % (current_thread().name, e)
                continue
    
                
        
