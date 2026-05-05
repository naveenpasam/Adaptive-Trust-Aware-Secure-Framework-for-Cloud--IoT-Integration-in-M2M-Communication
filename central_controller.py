import time
import numpy as np

class TrustEvaluationModule:
    def __init__(self, alpha=0.4, beta=0.4, gamma=0.2, decay_lambda=0.8):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.decay_lambda = decay_lambda
        
        # In-memory storage for device trust data
        self.device_trust_data = {}

    def _init_device(self, device_id):
        if device_id not in self.device_trust_data:
            self.device_trust_data[device_id] = {
                "S_i": 1.0,  # Initial security history is perfect
                "T_i": 1.0,  # Initial trust score
            }

    def evaluate_trust(self, device_id, B_i, R_i):
        """
        Calculates and updates trust score based on:
        T_i = alpha*S_i + beta*B_i + gamma*R_i (Eq 1)
        and then updates history using Eq 2.
        """
        self._init_device(device_id)
        
        # Retrieve historical security score
        S_i = self.device_trust_data[device_id]["S_i"]
        
        # R_i is mapped to a score here (e.g., 1.0 if normal rate, lower if anomalous)
        # B_i is behavioral consistency
        
        # Calculate Current Trust Evaluation (Eq 1)
        current_eval = self.alpha * S_i + self.beta * B_i + self.gamma * R_i
        
        # Update using historical decay (Eq 2)
        # T_i(t+1) = lambda * T_i(t) + (1 - lambda) * Delta_i
        # Here Delta_i is represented by our current_eval of recent behavioral variations
        T_i_t = self.device_trust_data[device_id]["T_i"]
        new_T_i = self.decay_lambda * T_i_t + (1 - self.decay_lambda) * current_eval
        
        # Update records
        self.device_trust_data[device_id]["T_i"] = new_T_i
        # S_i can be slowly updated based on T_i
        self.device_trust_data[device_id]["S_i"] = new_T_i
        
        return new_T_i


class AnomalyDetectionModule:
    def __init__(self, anomaly_threshold=2.0, window_size=10):
        self.anomaly_threshold = anomaly_threshold
        self.window_size = window_size
        self.device_request_history = {}
        self.last_update_time = time.time()
        
    def _init_device(self, device_id):
        if device_id not in self.device_request_history:
            self.device_request_history[device_id] = []

    def record_request_and_check_anomaly(self, device_id):
        """
        Records the request rate and calculates anomaly score A_i (Eq 3)
        A_i = |R_i - mu_R| / sigma_R
        """
        self._init_device(device_id)
        
        current_time = time.time()
        
        # Simple sliding window logic for request frequency over recent time
        history = self.device_request_history[device_id]
        history.append(current_time)
        
        # Keep only recent requests (e.g., within last 5 seconds to calculate rate)
        recent_requests = [t for t in history if current_time - t <= 5.0]
        self.device_request_history[device_id] = recent_requests
        
        R_i = len(recent_requests)
        
        # To calculate mu_R and sigma_R, we look at global average request rates 
        # For simplicity in simulation, we maintain a running global list of recent R_i
        all_rates = [len(reqs) for reqs in self.device_request_history.values() if len(reqs) > 0]
        
        if len(all_rates) <= 1 or np.std(all_rates) == 0:
            return False, 1.0 # Not anomalous, R_i score = 1.0
            
        mu_R = np.mean(all_rates)
        sigma_R = np.std(all_rates)
        
        # Calculate A_i
        A_i = abs(R_i - mu_R) / sigma_R
        
        is_anomalous = A_i > self.anomaly_threshold
        
        # R_i score mapping for Trust Evaluation:
        # If A_i is high (anomalous), R_i score is low.
        R_i_score = max(0.0, 1.0 - (A_i / (self.anomaly_threshold * 2)))
        
        return is_anomalous, R_i_score


class DeceptionModule:
    def __init__(self):
        pass
        
    def handle_malicious_request(self, data):
        """
        Directs low-trust devices to controlled responses.
        Avoids data leaking but deceives attackers.
        """
        device_id = data.get("device_id", "Unknown")
        # Return a fake successful response to deceive the attacker
        return {
            "status": "success",
            "message": "Data processed successfully (Deception Mode)",
            "action": "DECEPTION"
        }


class AccessControlModule:
    def __init__(self, T_min=0.6):
        self.T_min = T_min
        
    def check_access(self, T_i):
        """Grants access if T_i >= T_min"""
        return T_i >= self.T_min


class CentralController:
    """
    Central Controller integrating Trust Evaluation, Anomaly Detection,
    Access Control, and Deception Modules.
    """
    def __init__(self, cloud_layer):
        self.cloud_layer = cloud_layer
        self.trust_evaluator = TrustEvaluationModule()
        self.anomaly_detector = AnomalyDetectionModule()
        self.access_controller = AccessControlModule()
        self.deception_module = DeceptionModule()
        
    def handle_request(self, data, behavior_score):
        device_id = data["device_id"]
        
        # 1. Anomaly Detection
        is_anomalous, R_i_score = self.anomaly_detector.record_request_and_check_anomaly(device_id)
        
        if is_anomalous:
            # Drop behavior score severely if an anomaly is detected
            behavior_score *= 0.1 
            
        # 2. Trust Evaluation
        T_i = self.trust_evaluator.evaluate_trust(device_id, B_i=behavior_score, R_i=R_i_score)
        
        # 3. Access Control
        if self.access_controller.check_access(T_i):
            # Access Granted -> Forward to Cloud Layer
            response = self.cloud_layer.store_data(data)
            return {"device": device_id, "T_i": round(T_i, 3), "status": "Granted", "cloud_response": response}
        else:
            # Access Denied -> Route to Deception Module
            deception_response = self.deception_module.handle_malicious_request(data)
            return {"device": device_id, "T_i": round(T_i, 3), "status": "Denied/Deceived", "deception_response": deception_response}
