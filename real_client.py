import requests
import time
import random

SERVER_URL = "http://127.0.0.1:8000/api/upload"

def send_request(device_id, is_malicious):
    """Sends a real HTTP POST request to the FastAPI Edge Gateway."""
    
    # Generate the simulated payload
    payload_str = f"Telemetry data from {device_id}: {random.uniform(20.0, 30.0):.2f}C"
    
    # Generate behavioral consistency score (in real life, the server does this)
    if is_malicious:
        behavior_score = random.uniform(0.1, 0.5)
    else:
        behavior_score = random.uniform(0.8, 1.0)
        
    data = {
        "device_id": device_id,
        "timestamp": time.time(),
        "payload": payload_str,
        "request_type": "data_upload",
        "behavior_score": behavior_score
    }
    
    try:
        response = requests.post(SERVER_URL, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "Granted":
                print(f"[{device_id}] SUCCESS -> Data uploaded.")
            else:
                # This will print the Deception module's fake success message!
                deception = result.get("deception_response", {})
                print(f"[{device_id}] {deception.get('message')}")
        else:
            print(f"[{device_id}] Server Error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"[{device_id}] Could not connect to server. Is real_server.py running?")

def run_client_simulation():
    print("Starting Real-World Client Network Simulation...")
    print("This script is sending REAL network requests to http://127.0.0.1:8000")
    print("-" * 50)
    
    for step in range(1, 11):
        print(f"\n--- Network Step {step} ---")
        
        # 1. Normal device sends 1 request
        send_request("physical_thermostat_1", is_malicious=False)
        
        # 2. Malicious device launches DDoS flood (3-5 requests instantly)
        num_attacks = random.randint(3, 5)
        for _ in range(num_attacks):
            send_request("hacked_camera_x", is_malicious=True)
            
        time.sleep(1.0) # Wait a second before next step

if __name__ == "__main__":
    run_client_simulation()
