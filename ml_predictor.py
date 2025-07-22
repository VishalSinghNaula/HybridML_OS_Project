import socket
import joblib
import numpy as np
import pandas as pd 
import psutil

model = joblib.load("thread_predictor.pkl")


FEATURE_NAMES = ['cpu', 'wait', 'conflict', 'priority', 'deadline'] 

def get_system_state():
    """Get current system metrics"""
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return {
        'cpu_load': cpu,
        'memory_load': mem,
        'overall': 'overloaded' if cpu > 90 or mem > 90 else 
                  'stressed' if cpu > 70 or mem > 70 else 
                  'healthy'
    }

HOST, PORT = "localhost", 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"ML Predictor running on {PORT}")

    while True:
        conn, addr = s.accept()
        with conn:
            data = conn.recv(1024).decode().strip()
            if not data:
                continue

            try:
                # Parse features
                features = list(map(float, data.split(',')))
                
                # Create DataFrame with proper feature names
                X = pd.DataFrame([features], columns=FEATURE_NAMES) 
                
                # Get system state for logging (optional)
                system_state = get_system_state()
                print(f"Predicting for {features} | System: {system_state['overall']}")
                
                # Make prediction
                prediction = model.predict(X)[0] 
                conn.sendall(str(prediction).encode())
                
            except Exception as e:
                print(f"Error: {e}")
                conn.sendall(b"error")