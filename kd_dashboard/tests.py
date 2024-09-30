import pyodbc

import json
import pandas as pd


def get_settings_from_db(station_code):
    CONFIG_DATA = json.loads(open('config.json').read())
    DB = CONFIG_DATA['DATABASE']

    conn_str = (
        r'DRIVER={SQL Server};'
        rf'SERVER={DB['ip']};'
        rf'DATABASE={DB['db_name']};'
        rf'UID={DB['user']};'
        rf'PWD={DB['pwd']};'
    )
    conn = pyodbc.connect(conn_str)
    print(f"{DB['ip']} connected")

    query = f"exec [pydashboard_get_settings] {station_code}"
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    print(df)

    df.to_csv(f'{station_code}_settings')

get_settings_from_db('OP30')