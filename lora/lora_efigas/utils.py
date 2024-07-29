from .models import *
import struct

def parse_gas_meter_message(message):
    # Convert the hexadecimal string to bytes
    message_bytes = bytes.fromhex(message)
    parsed_data={}
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



################ CONSUMO-CALIBRACIÓN #####################


def generate_consumption(cubic_meters):
    # Command code for SBAL
    cmd_code = 0x05  
    
    # Frame identifier for downlink (assumed value, please replace with the correct one if different)
    frame_id = 0x01  # Assuming this is a downlink frame
    
    # Convert cubic meters to the unit of 0.001 cubic meters and cast to a signed integer
    purchase_value = int(cubic_meters * 1000)  # Convert m^3 to 0.001 m^3 units
    
    # Pack the purchase value as a 4-byte signed integer in little endian
    arg_payload = struct.pack('<i', purchase_value)
    
    # Construct the complete payload
    payload = struct.pack('<B', cmd_code) + arg_payload + struct.pack('<B', frame_id)
    
    return payload.hex()


################# SALDO ####################

def generate_balance(cubic_meters):
    # Command code for SBAL
    cmd_code = 0x0c  # Assuming 0x0C is the command for SBAL
    
    # Frame identifier for downlink (assumed value, please replace with the correct one if different)
    frame_id = 0x01  # Assuming this is a downlink frame
    
    # Convert cubic meters to the unit of 0.001 cubic meters and cast to a signed integer
    purchase_value = int(cubic_meters * 1000)  # Convert m^3 to 0.001 m^3 units
    
    # Pack the purchase value as a 4-byte signed integer in little endian
    arg_payload = struct.pack('<i', purchase_value)
    
    # Construct the complete payload
    payload = struct.pack('<B', cmd_code) + arg_payload + struct.pack('<B', frame_id)
    
    return payload.hex()

################ CAMBIO DE TIEMPO EN LOS REPORTES #####################


def set_time_repports(time):
    cmd_code = 0x06
    frame_id = 0x01 
    arg_payload = struct.pack('<H', int(time))
    payload = struct.pack('<B', cmd_code) + arg_payload+ struct.pack('<B', frame_id)
        # Convert the byte data to a hex string
    hex_payload = payload.hex()
    print(hex_payload)
    return hex_payload

################ TEMPERATURA #####################
def query_temp():
    cmd_code = 0x0d
    frame_id = 0x01 
    payload = struct.pack('<B', cmd_code) + struct.pack('<B', frame_id)
    hex_payload = payload.hex()
    return hex_payload
