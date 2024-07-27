from .models import *

def parse_gas_meter_message(message):
    # Convert the hexadecimal string to bytes
    message_bytes = bytes.fromhex(message)

    # Extract data according to specified byte positions and lengths
    cmd = message_bytes[0]
    accumulated_flow = int.from_bytes(message_bytes[1:5], byteorder='little')
    total_flow = int.from_bytes(message_bytes[5:9], byteorder='little')
    meter_status = message_bytes[9]
    alarm = message_bytes[10]
    battery_level = int.from_bytes(message_bytes[11:13], byteorder='little')
    rssi = message_bytes[13]
    snr = message_bytes[14]

    # Format battery level in 0.01V
    battery_voltage = battery_level * 0.01

    # Create a dictionary to return the parsed data
    parsed_data = {
        'Command': cmd,
        'Accumulated Flow (L)': accumulated_flow,
        'Total Flow (L)': total_flow,
        'Meter Status': meter_status,
        'Alarm': alarm,
        'Battery Voltage (V)': battery_voltage,
        'RSSI': rssi,
        'SNR': snr
    }

    return parsed_data

def save_gas_meter_data(parsed_message, dev_eui):
    if parsed_message['Command'] == 2:
        GasMeterData.objects.create(
            dev_eui=dev_eui,
            accumulated_flow=parsed_message['Accumulated Flow (L)'],
            total_flow=parsed_message['Total Flow (L)'],
            meter_status=parsed_message['Meter Status'],
            alarm=parsed_message['Alarm'],
            battery_voltage=parsed_message['Battery Voltage (V)'],
            rssi=parsed_message['RSSI'],
            snr=parsed_message['SNR']
        )




