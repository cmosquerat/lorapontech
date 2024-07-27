from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import base64
from .utils import *

@csrf_exempt
@require_POST
def receive_data(request):
    try:
        # Load JSON from request
        data_json = json.loads(request.body.decode('utf-8'))
        # Extract the base64 encoded data field
        b64_data = data_json.get('data', '')
        # Extract DevEUI
        dev_eui = data_json.get('deviceInfo', {}).get('devEui', 'No DevEUI found')
        # Decode and convert the base64 data
        decoded_hex = decode_and_convert_data(b64_data)
        # Print the decoded hexadecimal data and DevEUI for debugging
        print(f"DevEUI: {dev_eui}, Decoded Data: {decoded_hex}")
        parsed_message = parse_gas_meter_message(decoded_hex)
        print(parsed_message)
        save_gas_meter_data(parsed_message,dev_eui)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({
        'status': 'received',
        'DevEUI': dev_eui,
        'decoded_data': decoded_hex
    }, status=200)

def decode_and_convert_data(b64_data):
    # Decode base64 data
    decoded_bytes = base64.b64decode(b64_data)
    # Convert decoded bytes to hexadecimal
    hex_data = decoded_bytes.hex()
    return hex_data





#################### CONTROL VALVULA ##############################


class ValveControl(APIView):
    def post(self, request, *args, **kwargs):
        deveui = request.data.get('deveui')
        state = request.data.get('state')

        if deveui is None or state is None:
            return Response({"error": "Missing 'deveui' or 'state'"}, status=status.HTTP_400_BAD_REQUEST)

        # Determinar el valor de 'data' basado en el estado
        if state == "1":
            payload_data = "BFUB"
        elif state == "0":
            payload_data = "BJkB"
        else:
            return Response({'error': 'Invalid state value'}, status=status.HTTP_400_BAD_REQUEST)

        # Construir el cuerpo del POST request
        json_data = {
            "queueItem": {
                "confirmed": False,
                "data": payload_data,
                "fCntDown": 0,
                "fPort": 1,
                "isPending": True
            }
        }
        headers = {
            'accept': 'application/json',
            'Grpc-Metadata-Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJjaGlycHN0YWNrIiwiaXNzIjoiY2hpcnBzdGFjayIsInN1YiI6ImM4NmRiM2VmLTZhY2QtNDE1NS1hZmQ1LTAzNzAyNjM2NmZmMCIsInR5cCI6ImtleSJ9.1erH-6qO_DZjRahATSQulG-cbpbTyxtLB5Xg40G86vI',
            'Content-Type': 'application/json'
        }

        # Realizar la solicitud POST
        response = requests.post(f'https://lora.datalandia.site/api/devices/{deveui}/queue', json=json_data, headers=headers)

        # Comprobar si la solicitud fue exitosa
        if response.status_code == 200:
            return Response({"message": "Request successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send data to device"}, status=response.status_code)