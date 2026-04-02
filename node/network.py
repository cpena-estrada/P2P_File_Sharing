# network.py

import requests
import time


peers = []         # set by main.py at startup — ["localhost:5001", "localhost:5002"]
online_peers = []  # updated every loop


def ping_peers():
    """
    Goes through every known peer, tries to hit their /health endpoint.
    Updates online_peers list based on who responds.
    """
    global online_peers
    alive = []

    for peer in peers:
        try:
            response = requests.get(f"http://{peer}/health", timeout=2)
            if response.status_code == 200:
                alive.append(peer)
        except:
            pass  # peer is offline, just skip it

    online_peers = alive


def heartbeat_loop(interval: int = 5):
    """
    Runs forever. Pings peers every 'interval' seconds.
    """
    while True:
        ping_peers()
        time.sleep(interval)


def replicate(file_name: str, text: str, timestamp: float, written_by: str):
    for peer in online_peers:
        try:
            requests.post(
                f"http://{peer}/sync/{file_name}",
                json={
                    'text': text,
                    'incoming_timestamp': timestamp,
                    'written_by': written_by
                }
            )
        except:
            pass  # peer went offline between heartbeat and replication, skip it