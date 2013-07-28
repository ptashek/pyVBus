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
from logger.DataLogger import DataLogger
import json

class JSONLogger(DataLogger):

    def __init__(self, dst, keys=None):
        super(JSONLogger, self).__init__(dst, keys)
        self.json_dst = open(dst, 'a+')

    def __exit__(self, type, value, traceback):
        if not self.dst.closed:
            self.json_dst.flush()
            self.json_dst.close()
            

    def write_data(self, data):
        if self.keys:
            filter = [key for key in data.keys() if key not in self.keys]
            for key in filter:
                del data[key]

        line = json.dumps(data)
        if not line[-1:] == '\n':
            line += '\n'
        self.json_dst.write(line)

if __name__ == '__main__':
    exit(1)
