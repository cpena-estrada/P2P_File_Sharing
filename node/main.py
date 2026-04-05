# main.py

import uvicorn
import argparse
import threading
from routes import app
from store import FileStore
import routes, network


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    parser.add_argument('--peers', nargs='*', default=[])  # nargs='*' means 0 or more values
    args = parser.parse_args()
 
    # set variables for this node
    file_store = FileStore(node_name=f'node_{args.port}')
    routes.store = file_store
    routes.port = args.port
    network.peers = args.peers

    # declare and start thread to run heartbeat_loop function in the background
    t = threading.Thread(target=network.heartbeat_loop, daemon=True)
    t.start()

    # start up this node:
    network.sync_on_start_up()
    uvicorn.run(app, host="0.0.0.0", port=args.port)