import os
from django.shortcuts import render
from opcua import Client
import json
from kd_dashboard import opcua_data_collector as odc
import threading
import pyodbc
# Create your views here.
from django.http import JsonResponse
import pandas as pd
from datetime import datetime

config_file = 'config_MA.json'


def machine_allocation_settings(conn):
    try:
        print("machine allocation settings request")
        query = f"select * from py_machine_allocation_settings"
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        print(df)
        df.to_csv('buffer_settings/station_allocation_settings.csv')
        return True
    except Exception as e:
        print(f" Machine Allocation settings error : {e}")
        return False

def machine_settings(conn, station_code):
    try:
        query = f"exec [pydashboard_get_settings] {station_code}"
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]
        df = pd.DataFrame.from_records(rows, columns=columns)
        print(df)
        if df.shape[0] < 1:
            print(f"return empty set for settings {station_code} ")
            return False
        df.to_csv(f'buffer_settings/{station_code}_settings.csv')

        return True
    except:
        return False

def get_settings_from_db(station_code, q_type):
    print("request for settings")
    try:
        CONFIG_DATA = json.loads(open(config_file).read())
        DB = CONFIG_DATA['DATABASE']
        conn_str = (
            r'DRIVER={SQL Server};'
            rf'SERVER={DB['server']};'
            rf'DATABASE={DB['db_name']};'
            rf'UID={DB['user']};'
            rf'PWD={DB['pwd']};'
        )
        conn = pyodbc.connect(conn_str)
        print(f"{DB['server']} connected")
        if q_type == 'station_settings':
           print(f"station settings retrival successful for {station_code}") if machine_settings(conn, station_code) else print(f"station settings retrival failed for {station_code}")
        elif q_type == 'allocation_settings':
           print(f"machine_allocation settings retrival successful for {station_code}") if machine_allocation_settings(conn) else print(f"machine_allocation settings retrival failed for {station_code}")
        return True
    except Exception as e:
        print(e)
        return False

def query_pandas(station_name, var):
    try:
        variant = 'V' + str(var)
        df_settings = pd.read_csv(f'buffer_settings/{station_name}_settings.csv')
        df_settings = df_settings.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
        variant_filter = df_settings['Variant_Code'] == variant
        machine_filter = df_settings['AssetName'] == station_name
        filtered_df = df_settings[machine_filter & variant_filter]
        variant_name = filtered_df['VariantName'].tolist()[0]
        station_full_name = filtered_df['AssetDescription'].tolist()[0]
        variant_path = filtered_df['RecipeName'].tolist()[0]
        return variant_name, station_full_name , variant_path
    except Exception as e:
        print(f"Query pandas error {e}")
        return 'XXXX', 'XXXX' , 'XXXX'


def create_objects():
    try:
        CONFIG_DATA = json.loads(open(config_file).read())
        print("Last Program validated on on 21-08-2024")
        for server in CONFIG_DATA:
            if server != 'DATABASE':
                globals()[server] = odc.opcua_monitor(CONFIG_DATA[server], server)
                threading.Thread(target=globals()[server].connect_server).start()
                print(server, "object created")
    except Exception as e:
        print(e)


create_objects()


def get_shift():
    c_time = datetime.now()
    s1_start_time = datetime.strptime(str(datetime.now()).split(' ')[0] + ' 7:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    s2_start_time = datetime.strptime(str(datetime.now()).split(' ')[0] + ' 15:30:00.000', '%Y-%m-%d %H:%M:%S.%f')
    s3_start_time = datetime.strptime(str(datetime.now()).split(' ')[0] + ' 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    if s1_start_time <= c_time <= s2_start_time:
        return 'S1'
    elif s3_start_time <= c_time <= s1_start_time:
        return 'S3'
    else:
        return 'S2'


def get_plc_data(request, plc_name, station_name):
    all_plc_tags = globals()[plc_name].all_tags
    station_tags = {}
    for tag_name, value in all_plc_tags.items():
        if tag_name.find(station_name) != -1:
            station_tags[tag_name.split('|')[-1]] = value
    variant_name, station_name , variant_path = query_pandas(station_name, station_tags['model_no'])
    try:
        print(station_tags['model_no'])
    except:
        station_tags['model_no'] = 0

    station_tags['station_name'] = station_name
    station_tags['variant_name'] = variant_name
    station_tags['variant_path'] = variant_path
    station_tags['shift'] = get_shift()


    # try:
    #     if 'Alm' not in station_tags:
    #         station_tags['Alm'] = {'' :'No live alarms' }
    # except:
    #     if len(station_tags['Alm'])  < 1:
    #         station_tags['Alm'] = {'': 'No live alarms'}





    return JsonResponse(station_tags, safe=False)


def main_page(request, plc_name, station_code):
    context = {
        'plc_name': plc_name,
        'station_name': station_code,
        'db_response': get_settings_from_db(station_code, 'station_settings'),
        'client_ip': 'Admin Page',
        "alarms": "ALMS"
    }
    return render(request, 'index.html', context)
    # return JsonResponse({"hello": station_name}, safe=False)


def hourly_call(request, station_code):
    CONFIG_DATA = json.loads(open(config_file).read())
    DB = CONFIG_DATA['DATABASE']
    conn_str = (
        r'DRIVER={SQL Server};'
        rf'SERVER={DB['server']};'
        rf'DATABASE={DB['db_name']};'
        rf'UID={DB['user']};'
        rf'PWD={DB['pwd']};'
    )

    conn = pyodbc.connect(conn_str)
    print(f"{DB['server']} connected")
    query = f"exec pydashboard_hourly {station_code}"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    hourly_dict = {
        '1': ['0', '0'],
        '2': ['0', '0'],
        '3': ['0', '0'],
        '4': ['0', '0'],
        '5': ['0', '0'],
        '6': ['0', '0'],
        '7': ['0', '0'],
        '8': ['0', '0'],
    }
    for row_number in range(len(df)):
        row = df.iloc[row_number]
        hourly_dict[str(row['hour'])] = [str(row['actual']), str(row['planned'])]

    return JsonResponse(hourly_dict, safe=False)


def get_allocation(pc_ip):
    df_settings = pd.read_csv(f'buffer_settings/station_allocation_settings.csv')
    ip_filter = df_settings['pc_ip'] == pc_ip
    filtered_df = df_settings[ip_filter]

    if filtered_df.shape[0] > 0:
        operation = filtered_df['operation'].tolist()[0]
        plc = filtered_df['plc_name'].tolist()[0]
        return [True, operation, plc]
    else:
        return [False, '-', '-']


def allocated_dashboard(request):
    get_settings_from_db('None', 'allocation_settings')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = None
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    station_list = get_allocation(ip)
    if station_list[0]:
        print(f"Dashboard {station_list[1]} allocated for this IP {ip}")
        context = {
            'plc_name': station_list[2],
            'station_name': station_list[1],
            'db_response': get_settings_from_db(station_list[1], 'station_settings'),
            'client_ip': ip,

            "alarms": "ALMS"
        }
        return render(request, 'index.html', context)
    else:
        print(f"Cant allocate Dashboard for this IP {ip}")
        return JsonResponse({"": "This PC IP is not configured"}, safe=False)

#  python manage.py runserver 10.141.45.203:8000
