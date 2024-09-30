import threading
import time
from opcua import Client
import csv, json, os
from datetime import datetime
import shutil, sys


def get_run_time(func):
    def wrapper(*args):
        start_time = datetime.now()
        func(*args)
        time_taken = datetime.now() - start_time
        print(f"Time taken for {func} is {time_taken}")

    return wrapper


class opcua_monitor:
    def __init__(self, DATA, server):
        self.tag_not_found_list = None
        self.endpoint_con_status = None
        sys.excepthook = self.default_exception_handler
        self.station = server
        self.server_config = DATA['server_config']
        self.tags = DATA['tags']
        self.client = None
        self.connection_retry_time = 5
        self.all_tags = {}
        self.buffer_alarm_data = {}
        self.create_tags()

        # self.connect_server()

    def default_exception_handler(self, exc_type, exc_value, exc_traceback):
        print(f"Default exception Handler")
        print(f' Exc type : {exc_type}')
        print(f' Exc Value :{exc_value}')

        for i in range(10):
            print(f'This window for {self.server_config['end_point']} close in {10 - i} sec')
            time.sleep(1)

    def create_tags(self):
        for tag in self.tags:
            self.buffer_alarm_data[tag.split('|')[0]] = {}
            globals()[tag] = None
        print(self.buffer_alarm_data)

    def connect_server(self):
        print("Thread Started ...1")
        try:
            self.client = Client(self.server_config['end_point'])
            self.client.connect()
            self.endpoint_con_status = True
            print(
                f' ::: server initializing for end point {self.station}  is successful ::: - {datetime.now()}')
        except:
            print(
                f' ::: server initializing for end point {self.station}  is unsuccessful will be retry in 5 Sec ::: - {datetime.now()}')
        self.live_logger()

    def live_logger(self):
        while True:
            if self.endpoint_con_status:
                try:  # check for opcua connected
                    b = self.client.get_endpoints()
                    # self.all_tags['OP10|alms'] = [ 'yes i am error' , 'no i am error' , 'may be i am error' ]
                    for tag_name, tag in self.tags.items():

                        try:
                            if tag_name.split("|")[1] == 'Alm':
                                plc_live_alms = self.get_alarm_list(tag)
                                for alm, start_time in self.buffer_alarm_data[tag_name.split("|")[0]].items():
                                    if alm in plc_live_alms:
                                        plc_live_alms[alm] = start_time
                                self.buffer_alarm_data[tag_name.split("|")[0]] = plc_live_alms
                                self.all_tags[tag_name] = plc_live_alms

                            else:
                                node = self.client.get_node(tag)
                                self.all_tags[tag_name] = node.get_value()
                        except Exception as e:
                            self.all_tags[tag_name] = 'XXXX'
                except Exception as e:
                    print(e)
                    self.endpoint_con_status = False
            else:
                time.sleep(self.connection_retry_time)
                self.connect_server()

    def get_alarm_list(self, tag):
        instant_alms_list = {}
        try:
            alarm_nos = self.client.get_node(tag).get_children()
            for i in range(len(alarm_nos)):
                text = self.client.get_node(tag + f"[{i}].\"alarmText\"").get_value()
                currentState = self.client.get_node(tag + f"[{i}].\"currentState\"").get_value()

                if text != "" and str(currentState) == 'True':
                    instant_alms_list[text] = str(datetime.now())

            return instant_alms_list
        except Exception as e:
            return {"error": e}


if __name__ == '__main__':
    try:
        CONFIG_DATA = json.loads(open('../config_MA.json').read())
        print("Last Program validated on on 29-07-2024")
        for server in CONFIG_DATA:
            globals()[server] = opcua_monitor(CONFIG_DATA[server], server)
            threading.Thread(target=globals()[server].connect_server).start()
        while True:
            time.sleep(5)
            print(globals()['Stn1'].all_tags)
    except Exception as e:
        print(e)
