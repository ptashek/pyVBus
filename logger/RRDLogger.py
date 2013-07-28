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
    Sample (and simple) RRD logger putting values straight into an RRD data store
    The assumption is that values are supplied in the correct order
'''
from logger.DataLogger import DataLogger
import rrdtool

class RRDLogger(DataLogger):

    def __init__(self, dst, keys=None):
        super(RRDLogger, self).__init__(dst, keys)

    def write_data(self, data):
        if self.keys:
            filter = [key for key in self.keys if key in data.keys()]
            values = map(lambda k: "%s" % data[k], filter)
        else:
            values = map(lambda v: "%s" % v, data.values())
        output = ":".join(values)
        rrdtool.update(self.dst, output)

if __name__ == 'main':
    exit(1)
