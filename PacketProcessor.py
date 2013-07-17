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
from sys import exit
from abc import abstractmethod
from threading import Thread
from Queue import Queue

class PacketProcessor(object):
    
    def __init__(self, num_workers, results_callback):
        self.work_q = Queue()
        self.result_q = Queue()
        self.num_workers = num_workers
        self.workers = []
        for i in range(self.num_workers):
            worker = Thread(target=self.process, name="worker-%s" % i)
            self.workers.append(worker)
        
        worker = Thread(target=results_callback, name="results-%s" % i)
        self.results = []
        self.results.append(worker)
    
    def is_alive(self):
        return len(self.workers) > 0
                   
    def put_packet(self, packet_bytes):
        self.work_q.put(packet_bytes)
            
    def start(self):
        workers = self.workers + self.results
        for worker in workers:
            worker.start()
            
    def stop(self):
        for i in range(self.num_workers):
            self.work_q.put(None)
            
        num_results = len(self.results)
        for i in range(num_results):
            self.result_q.put(None)
            
    @abstractmethod
    def process(self):
        raise NotImplementedError("The process() method is not implemented")
            
if __name__ == '__main__':
    exit(1)