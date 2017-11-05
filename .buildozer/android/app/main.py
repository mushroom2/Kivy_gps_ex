from kivy.lang import Builder
from plyer import gps, notification
from kivy.app import App
from kivy.properties import StringProperty
from kivy.clock import Clock, mainthread
import random
import json
from datetime import datetime
import requests
import os

kv = '''
BoxLayout:
    orientation: 'vertical'
    Label:
        text: app.gps_location
    Label:
        text: app.gps_status
    BoxLayout:
        size_hint_y: None
        height: '48dp'
        padding: '4dp'
        Button:
            text: 'Залить на сервер'
            on_release: app.post_coords()

    BoxLayout:
        size_hint_y: None
        height: '48dp'
        padding: '4dp'
        ToggleButton:
            text: 'Поехали!' if self.state == 'normal' else 'Stop'
            on_state:
                app.start(1000, 0) if self.state == 'down' else \
                app.stop()
'''


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


class gpsex(App):
    updtime = datetime.now()
    gps_location = StringProperty()
    gps_status = StringProperty('Click Start to get GPS location updates')
    data_dir = App().user_data_dir
    l = MyLogging(data_dir)
    postgeostore = []

    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        return Builder.load_string(kv)

    def start(self, minTime, minDistance):
        gps.start(minTime, minDistance)

    @mainthread
    def stop(self):
        try:
            gps.stop()
            self.l.write_data(json.dumps(self.postgeostore))
        except Exception as e:
            t = open(str(App().user_data_dir) + '/' + 'lll.txt', 'w')
            t.write(str(e))
            t.close()

    @mainthread
    def on_location(self, **kwargs):
        self.gps_location = '\n'.join(['{}={}'.format(k, v) for k, v in kwargs.items()])
        if len(self.postgeostore) <= 2 or (datetime.now() - self.updtime).seconds <= 30:
            self.postgeostore.append({'lat': kwargs['lat'], 'lng': kwargs['lon']})

    @mainthread
    def on_status(self, stype, status):
        self.gps_status = 'type={}\n{}'.format(stype, status)

    def on_pause(self):
        gps.stop()
        self.l.write_data(json.dumps(self.postgeostore))
        self.postgeostore = []
        return True

    def on_resume(self):
        gps.start(1000, 0)
        pass

    def post_coords(self):
        try:
            mr = []
            targetlogs = list(filter(lambda x: '.txt' in x and '_' in x, os.listdir(App().user_data_dir)))
            targetlogs.sort(key=lambda x: datetime.strptime(x.split('.')[0], '%d_%m_%y_%H_%M_%S'))
            for log in targetlogs:
                targetlog = open(App().user_data_dir + '/' + log, 'r')
                data = json.loads(targetlog.read() or '[]')
                targetlog.close()
                mr += data
            if mr:
                d = {
                    "track": mr,
                    "name": 'trackname' + datetime.now().strftime('%d_%m_%y_%H_%M_%S'),
                    "user": 'wilder',
                    "description": 'from Android app'
                }
                headers = {
                    'contentType': 'application/json; charset=utf-8',
                    'dataType': 'json'
                }
                requests.post('http://wilder.pythonanywhere.com/map/savetrack', json=d, headers=headers)
            kwargs = {'title': 'Fuck Yeeeah!', 'message': 'Yo coords upload on server!'}
            notification.notify(**kwargs)
            for log in targetlogs:
                os.remove(App().user_data_dir + '/' + log)
        except Exception as e:
            t = open(str(App().user_data_dir) + '/' + 'lll.txt', 'w')
            t.write(str(e))
            t.write(str(os.listdir(App().user_data_dir)))
            t.write(self.data_dir)
            t.write(os.name)
            t.close()


if __name__ == '__main__':
    gpsex().run()
