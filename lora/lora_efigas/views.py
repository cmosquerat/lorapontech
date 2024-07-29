from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import base64
from .utils import *
from .serializers import *
from django.db.models import OuterRef, Subquery, Max
from rest_framework.generics import ListAPIView


@csrf_exempt
@require_POST

def receive_data(request):
    try:
        data_json = json.loads(request.body.decode('utf-8'))
        # Extract the base64 encoded data field
        b64_data = data_json.get('data', '')
        # Extract DevEUI
        dev_eui = data_json.get('deviceInfo', {}).get('devEui', 'No DevEUI found')
        # Decode and convert the base64 data
        decoded_hex = decode_and_convert_data(b64_data)
        # Print the decoded hexadecimal data and DevEUI for debugging
        print(f"DevEUI: {dev_eui}, Decoded Data: {decoded_hex}")
        if decoded_hex[1]=="d":
                return JsonResponse({
                    'status': 'received',
                    'DevEUI': dev_eui,
                    'decoded_data': decoded_hex
                }, status=200)

        parsed_message = parse_gas_meter_message(decoded_hex)
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
        print(response)
        if response.status_code == 200:
            return Response({"message": "Request successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send data to device"}, status=response.status_code)
        




#################### PONER SALDO ##############################


class SetBalance(APIView):
    def post(self, request, *args, **kwargs):
        deveui = request.data.get('deveui')
        balance = request.data.get('balance')


        if deveui is None or balance is None:
            return Response({"error": "Missing 'deveui' or 'balance'"}, status=status.HTTP_400_BAD_REQUEST)
        

        try:
            balance = float(balance)  # Intenta convertir balance a entero
        except ValueError:
            return Response({"error": "Balance must be an float"}, status=status.HTTP_400_BAD_REQUEST)

        hex_values_specific = generate_balance(balance)
        bytes_from_hex_specific = bytes.fromhex(hex_values_specific)

        # Encode these bytes to base64
        payload_data = base64.b64encode(bytes_from_hex_specific)

        payload_data=payload_data.decode('utf-8')
       
        print(payload_data)
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
        

#################### PONER CONSUMO / CALIBRAR ##############################


class SetConsumption(APIView):
    def post(self, request, *args, **kwargs):
        deveui = request.data.get('deveui')
        consumption = request.data.get('consumption')


        if deveui is None or consumption is None:
            return Response({"error": "Missing 'deveui' or 'consumption'"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            consumption = float(consumption)  # Intenta convertir consumption a entero
            if consumption < 0:
                raise ValueError("Consumption must be a positive float")  # Asegura que sea positivo
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        hex_values_specific = generate_consumption(consumption)
        bytes_from_hex_specific = bytes.fromhex(hex_values_specific)

        # Encode these bytes to base64
        payload_data = base64.b64encode(bytes_from_hex_specific)
        payload_data=payload_data.decode('utf-8')
       

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
        


#################################### ESTADO MEDIDORES ##########################################

class LatestGasMeterDataView(APIView):
    def get(self, request):
        # First, get the latest timestamp for each dev_eui
        latest_per_dev_eui = GasMeterData.objects.values('dev_eui').annotate(
            latest_timestamp=Max('timestamp')
        )

        # Now, query all GasMeterData where the dev_eui and timestamp match these latest timestamps
        latest_entries = GasMeterData.objects.filter(
            dev_eui__in=[item['dev_eui'] for item in latest_per_dev_eui],
            timestamp__in=[item['latest_timestamp'] for item in latest_per_dev_eui]
        )

        # Serializing the data
        serializer = GasMeterDataSerializer(latest_entries, many=True)
        return Response(serializer.data)
    


#################################### Histórico de estados de un medidor ############################

class GasMeterDataListView(ListAPIView):
    serializer_class = GasMeterDataSerializer

    def get_queryset(self):
        """
        This view should return a list of all the GasMeterData
        for the currently authenticated user's dev_eui.
        """
        deveui = self.kwargs['deveui']  # Get the 'deveui' from the URL parameter
        return GasMeterData.objects.filter(dev_eui=deveui)


#################################### Configurar Tiempo de reporte ############################
class SetTime(APIView):
    def post(self, request, *args, **kwargs):
        deveui = request.data.get('deveui')
        time = request.data.get('time')


        if deveui is None or time is None:
            return Response({"error": "Missing 'deveui' or 'time'"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            time = float(time)  # Intenta convertir time a entero
            if time < 0:
                raise ValueError("time must be a positive float")  # Asegura que sea positivo
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        hex_values_specific = set_time_repports(time)
        bytes_from_hex_specific = bytes.fromhex(hex_values_specific)

        # Encode these bytes to base64
        payload_data = base64.b64encode(bytes_from_hex_specific)
        payload_data=payload_data.decode('utf-8')
       

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
#################################### Query temperatura medidor #####################################
class QueryTemp(APIView):
    def post(self, request, *args, **kwargs):
        deveui = request.data.get('deveui')

        if deveui is None:
            return Response({"error": "Missing 'deveui' or 'time'"}, status=status.HTTP_400_BAD_REQUEST)
        hex_values_specific = query_temp()
        bytes_from_hex_specific = bytes.fromhex(hex_values_specific)

        # Encode these bytes to base64
        payload_data = base64.b64encode(bytes_from_hex_specific)
        payload_data=payload_data.decode('utf-8')
       

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
#################################### Histórico de estados de un medidor ############################

class GasMeterDataListView(ListAPIView):
    serializer_class = GasMeterDataSerializer

    def get_queryset(self):
        """
        This view should return a list of all the GasMeterData
        for the currently authenticated user's dev_eui.
        """
        deveui = self.kwargs['deveui']  # Get the 'deveui' from the URL parameter
        return GasMeterData.objects.filter(dev_eui=deveui)

