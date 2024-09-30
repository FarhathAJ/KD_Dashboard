#
# from opcua import Client
#
#
# client = Client('"opc.tcp://10.141.44.130:4840"')
# client.connect()
#
#
#
# tag = "ns=3;s=\"IOTOP220DB\".\\\"IOTData\".\"alarm\""
#
#
#
#
#
# alarm_nos = client.get_node(tag).get_children()
# for i in range(len(alarm_nos)):
#     text = client.get_node(tag + f"[{i}].\"alarmText\"").get_value()
#     currentState = client.get_node(tag + f"[{i}].\"currentState\"").get_value()
#     if text != "" and str(currentState) == 'True':
#         print(text)
station_tags = {
    'ok_parts': 0, 'nok_parts': 112, 'cycle_time': 5.5269999504089355, 'model_no': 0, 'takt_time': 5.5269999504089355,
    'EngineData': '',
    'Alm': {'OP220-MA-MP5 Main Air Pressure Switch Feedback Error (I100.0)': '2024-08-26 15:50:01.401412'},
    'station_name': 'Spark Plug Tightening, Ignition coil assembly, IN/', 'variant_name': 'KD', 'shift': 'S2'}

print(station_tags['Alm'])
