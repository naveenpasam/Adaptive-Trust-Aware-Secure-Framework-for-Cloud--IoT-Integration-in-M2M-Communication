import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
import time

# Import your existing, unmodified core security logic
from central_controller import CentralController

# Import our new real MongoDB cloud layer
from real_mongodb_cloud import RealCloudLayer

app = FastAPI(title="Adaptive Trust-Aware Cloud-IoT Gateway")

# Initialize the architecture layers (Edge/Controller/Cloud)
cloud_db = RealCloudLayer("mongodb://localhost:27017/")
controller = CentralController(cloud_layer=cloud_db)

class IoTRequest(BaseModel):
    device_id: str
    timestamp: float
    payload: str
    request_type: str
    behavior_score: float # In a real implementation, the edge/server might calculate this based on packet inspection. Here, the client provides it for simulation purposes.

@app.post("/api/upload")
async def handle_iot_request(req: IoTRequest):
    """
    This endpoint acts as the Edge Node receiving the request, 
    and immediately passes it to the Central Controller.
    """
    # Convert Pydantic model back to the dict format expected by CentralController
    data_dict = {
        "device_id": req.device_id,
        "timestamp": req.timestamp,
        "payload": req.payload,
        "request_type": req.request_type
    }
    
    # Process request through your mathematical security brain
    response = controller.handle_request(data_dict, req.behavior_score)
    
    # Print real-time server logs
    t_i = response["T_i"]
    status = response["status"]
    
    if status == "Granted":
        cloud_info = response.get("cloud_response", {})
        print(f"[SERVER LOG] Granted Access for {req.device_id} | Trust: {t_i} | DB Total: {cloud_info.get('storage_size')}")
    else:
        deception_info = response.get("deception_response", {})
        print(f"[SERVER LOG] Blocked {req.device_id} | Trust: {t_i} | Action: {deception_info.get('action')}")
        
    return response

if __name__ == "__main__":
    print("Starting Real-World IoT Edge Gateway Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
