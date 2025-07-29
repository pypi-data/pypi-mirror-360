import json
import threading
import time
import requests
from .collector import flush
import os

is_kubernetes = os.getenv('KUBERNETES_SERVICE_HOST') is not None
agent_url = (
    'http://watchlog-node-agent:3774/apm'
    if is_kubernetes
    else 'http://localhost:3774/apm'
)
interval = 10


def send(metrics):
    try:
        payload = {
            "collected_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "platformName": 'flask',
            "metrics": metrics,
        }
        response = requests.post(agent_url, json=payload, timeout=3)
        if response.status_code >= 400:
            pass
            # print(f"[Watchlog APM] Agent error: {response.status_code}")
    except Exception as e:
        pass
        # print(f"[Watchlog APM] Send failed: {e}")


def start():
    def loop():
        while True:
            metrics = flush()
            if metrics:
                send(metrics)
            time.sleep(interval)

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
