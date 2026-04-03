# network.py

import requests
import time
import routes # import like this, not at 'from route import store' because that will import it at load time (when its None)


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


def heartbeat_loop(interval: int = 10):
    """
    Runs forever. Pings peers every 'interval' seconds.
    """
    while True:
        ping_peers()
        time.sleep(interval)


def replicate(file_name: str, text: str, timestamp: float, written_by: str):
    """
    Replicate/send a given file to all online peers

    Called by store.write_file()
    """
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

def sync_on_start_up():
    """
    Populate local storage by getting all files of all active peers
    """
    # ping peers to populate online_peers
    ping_peers()

    for peer in online_peers:
        # get list of files of every peer/node
        try:
            response = requests.get(f"http://{peer}/files")

            if response.status_code != 200:
                continue
            data = response.json()
            files = data['files']

            # get data of each file
            for file in files:

                response = requests.get(f"http://{peer}/files/{file}")
                file_data = response.json()

                text = file_data['text']
                timestamp = file_data['metadata']['timestamp']

                # write it locally
                if routes.store.is_newer(file, timestamp):
                    routes.store.write_file(file, text, timestamp) 
        except Exception as e:
            print(f"sync failed for {peer}: {e}")