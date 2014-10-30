'''
   Copyright 2013 Lukasz Szmit

   Licensed under the Apache License, Version 2.0 (the 'License');
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an 'AS IS' BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
from DeltaSolC import DeltaSolC
from argparse import ArgumentParser
from socket import socket, timeout, SOCK_STREAM, AF_INET, SOL_TCP
from time import sleep
import json
import daemon
import daemon.pidfile
import logging
import logging.handlers
import signal
import os, pwd, grp

class VBusListener():  
        
    def __init__(self):
        parser = ArgumentParser(description='Solar Controller Data Collector')
        parser.add_argument('-s', '--src', type=str, help='Controller IP Address')
        parser.add_argument('-p', '--port', type=int, help='Controller Port')
        parser.add_argument('-f', '--format', type=str, help='Data logger type', default='json')
        parser.add_argument('-d', '--dst', type=str, help='Data file', default='/tmp/vbus_data.log')      
        parser.add_argument('-P', '--pass', type=str, help='Password', default=None)      
        parser.add_argument('-k', '--keys', type=str, help='Comma delimited list of keys to dump', default=None)      
        parser.add_argument('-l', '--log', type=str, help='Debug log path', default='/tmp/vbus_debug.log')      
        parser.add_argument('-t', '--timeout', type=int, help='Socket timeout', default=5)      
        parser.add_argument('-u', '--user', type=str, help='System user to run as', default='vbus')      
        parser.add_argument('-g', '--group', type=str, help='System group to run as', default='vbus')      
        self.args = vars(parser.parse_args())

        try:
            if os.getuid() == 0:
                os.setgroups([])
                os.setgid(grp.getgrnam(self.args['user']).gr_gid)
                os.setuid(pwd.getpwnam(self.args['group']).pw_uid)
                os.umask(077)
        except:
            exit(255)

        self.__setup_logging()
   
        self.packet_processor = DeltaSolC(
            results_callback=self.write_data, 
            log_callback=self._log
        )
        
        if self.args['keys']:
            keys = self.args['keys'].split(',')
        else:
            keys = None

        if self.args['format'] == 'json':
            from logger.JSONLogger import JSONLogger 
            self.data_logger = JSONLogger(self.args['dst'], keys)
        elif self.args['format'] == 'rrd':
            from logger.RRDLogger import RRDLogger 
            self.data_logger = RRDLogger(self.args['dst'], keys)
        else:
            raise Exception('Unknown format type')

        signal.signal(signal.SIGTERM, self.__term_handler)

    def __term_handler(self, _signo, _stack_frame):
        self._log.info('TERM signal received. Quitting!');
        self.cleanup()
        exit(0)

    def __setup_logging(self):
        self._log = logging.getLogger(__name__)
        self._log.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(self.args['log'], maxBytes=1048576, backupCount=1)
        handler.setFormatter(logging.Formatter(
            fmt='%(asctime)s %(message)s', 
            datefmt='%d-%m-%Y %H:%M:%S'
        ))
        self._log.addHandler(handler)

    def write_data(self):
        result_q = self.packet_processor.result_q
        while True:
            result = result_q.get()
            if result is None:
                break
            self.data_logger.write_data(result)
   
    def cleanup(self):
        self.sock.close()
        self.packet_processor.stop()        

    def connect(self):
        while True:
            try:
                self.sock = socket(AF_INET, SOCK_STREAM, SOL_TCP)
                self.sock.settimeout(self.args['timeout'])
                vbus = (self.args['src'], self.args['port'])
                self._log.info('Connecting to %s:%s' % vbus)
                self.sock.connect(vbus)
                break
            except timeout as e:
                self._log.exception('Retrying: %s' % e)
                self.sock.close()
                sleep(5)
                continue

    def run(self):
        self.connect()
        self.packet_processor.start()
        
        while True:
            try:
                while self.packet_processor.is_alive():
                    r = self.sock.recv(1024)
                    if len(r) == 0:
                        self._log.error('No data received!')
                        self.sock.close()
                        self.connect()
                        continue
                            
                    if '+HELLO' in r:                
                        self.sock.sendall('PASS %s' % self.args['pass'])
                        continue
                            
                    if '+OK: Password accepted' in r:
                        self.sock.sendall('DATA')
                        continue
                                      
                    if '+OK: Data incoming...' in r:
                        self._log.info('Connected!')             
                
                    d = ''
                    ''' The fun part '''
                    while True:
                        r = self.sock.recv(1024)
                        if len(r) == 0:
                            self._log.error('No data received!')
                            self.connect()
                            break

                        d += r
                        if '\xaa' in d:
                            try:
                                s = d.index('\xaa')
                                e = d[s + 1:].index('\xaa')
                                p = d[s:e + 1]
                                d = d[e + 1:]                         
                                self.packet_processor.put_packet(p)
                            except ValueError:
                                continue
            except Exception as e:
                self._log.exception(e)
                self.sock.close()
                self.connect()
                continue
        
if __name__ == '__main__':
    pidfile = daemon.pidfile.PIDLockFile('/var/run/vbusd.pid')
    with daemon.DaemonContext(pidfile=pidfile):
        vbus_listener = VBusListener()
        vbus_listener.run()
    vbus_listener.cleanup()
    exit(0)
