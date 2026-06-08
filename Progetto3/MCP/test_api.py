"""
Simple script to test the local FastAPI Backend API.
Queries the local server using httpx.
"""

import httpx
import json

URL = "http://127.0.0.1:8000/career-path"
PAYLOAD = {"job": "cuoco"}

print(f"🚀 Inviando richiesta POST a {URL}...")
print(f"📦 Payload: {json.dumps(PAYLOAD)}\n")

try:
    # Set a large timeout as Ollama local inference takes a few seconds
    response = httpx.post(URL, json=PAYLOAD, timeout=60.0)
    
    print(f"📡 Status Code: {response.status_code}")
    print("-" * 50)
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Risposta ricevuta con successo:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Errore (Status {response.status_code}):")
        print(response.text)
except Exception as e:
    print(f"❌ Impossibile stabilire una connessione con il backend: {e}")
    print("Verifica che shiftx_backend_api.py sia in esecuzione su un altro terminale.")
