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
from DataLogger import DataLogger
from DeltaSolC import DeltaSolC
from argparse import ArgumentParser
from socket import socket, SOCK_STREAM, AF_INET, SOL_TCP
from sys import exit
from time import sleep

class VBusListener():  
        
    def __init__(self):
        parser = ArgumentParser(description="Solar Controller Data Collector")
        parser.add_argument('-s', '--src', type=str, help="Controller IP Address")
        parser.add_argument('-p', '--port', type=int, help="Controller Port")
        parser.add_argument('-f', '--file', type=str, help="Data file", default='/tmp/vbus_data.log')      
        parser.add_argument('-P', '--pass', type=str, help="Password", default=None)      
        self.args = vars(parser.parse_args())
   
        self.packet_processor = DeltaSolC(self.log)
        self.data_logger= DataLogger(self.args["file"])
        self.sock = socket(AF_INET, SOCK_STREAM, SOL_TCP)
        self.sock.settimeout(5.0)

    def log(self):
        result_q = self.packet_processor.result_q
        while True:
            result = result_q.get()
            if result is None:
                break
            self.data_logger.write_data(result)
   
    def cleanup(self):
        self.sock.close()
        self.packet_processor.stop()        
            
    def run(self):
        vbus = (self.args["src"], self.args["port"])
        print "Connecting to %s:%s" % vbus
        
        while True:
            try:
                self.sock.connect(vbus)
                break
            except socket.error as e:
                print "Retrying... %s" % e
                sleep(5)
                continue
   
        self.packet_processor.start()
            
        while True and self.packet_processor.is_alive():
                r = self.sock.recv(1024)
                if not r:
                    continue
                        
                if "+HELLO" in r:                
                    self.sock.sendall("PASS %s" % self.args["pass"])
                    continue
                        
                if "+OK: Password accepted" in r:
                    self.sock.sendall("DATA")
                    continue
                                  
                if "+OK: Data incoming..." in r:
                    print "Connected!"              
            
                d = ''
                ''' The fun part '''
                while True:
                    d += self.sock.recv(1024)
                    if '\xaa' in d:
                        try:
                            s = d.index('\xaa')
                            e = d[s + 1:].index('\xaa')
                            r = d[s:e + 1]
                            d = d[e + 1:]                         
                            self.packet_processor.put_packet(r)
                        except ValueError:
                            continue
    
if __name__ == '__main__':
    try:
        vbus_listener = VBusListener()
        vbus_listener.run()
    except KeyboardInterrupt:
        vbus_listener.cleanup()
        exit(1)
