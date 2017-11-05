from datetime import datetime
import json


class MyLogging:
    t = datetime.now()

    def __init__(self, path):
        self.f = open(str(path) + '/' + self.t.strftime('%d_%m_%y_%H_%M_%S')+'.txt', 'w+')
        self.boof = ''
        self.path = str(path)

    def write_data(self, data):
        if self.f.closed:
            self.f = open(self.f.name, 'w+')
        if self.boof:
            data = json.dumps(json.loads(self.boof) + json.loads(data))
        self.f.write(data)
        self.boof = data
        self.close()

    def close(self):
        self.f.close()



import os


m = MyLogging('.')
m.write_data(json.dumps([{'1': '2'}]))
m.write_data(json.dumps([{'3': '5'}]))

