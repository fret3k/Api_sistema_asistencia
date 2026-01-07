import requests
from datetime import datetime

base_url = "http://127.0.0.1:8000"
endpoint = "/reportes/mensual"

today = datetime.now()
mes = today.month
anio = today.year

print(f"Testing {base_url}{endpoint} with mes={mes} anio={anio}")

try:
    response = requests.get(f"{base_url}{endpoint}", params={"mes": mes, "anio": anio})
    if response.status_code == 200:
        print("Success!")
        data = response.json()
        print(f"Received {len(data)} records.")
        if data:
            print("First record sample:")
            print(data[0])
    else:
        print(f"Failed with status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception: {e}")
