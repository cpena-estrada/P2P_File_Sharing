# Deployment Guide

This project has two parts:

- the backend nodes in `node/`
- the frontend in `frontend/`

The frontend is just a static site. The backend is a FastAPI app that you run once per node.

## Before you start

From the project root:

```bash
cd /home/henry/Projects/school/P2P_File_Sharing
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you already have `.venv` set up, you only need:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the backend nodes

Open three terminals.

In terminal 1:

```bash
cd /home/henry/Projects/school/P2P_File_Sharing
source .venv/bin/activate
cd node
python3 main.py --port 8000 --peers 127.0.0.1:8001 127.0.0.1:8002
```

In terminal 2:

```bash
cd /home/henry/Projects/school/P2P_File_Sharing
source .venv/bin/activate
cd node
python3 main.py --port 8001 --peers 127.0.0.1:8000 127.0.0.1:8002
```

In terminal 3:

```bash
cd /home/henry/Projects/school/P2P_File_Sharing
source .venv/bin/activate
cd node
python3 main.py --port 8002 --peers 127.0.0.1:8000 127.0.0.1:8001
```

If everything is running, each terminal should show Uvicorn startup logs.

## Run the frontend

Open a fourth terminal:

```bash
cd /home/henry/Projects/school/P2P_File_Sharing/frontend
python3 -m http.server 8080
```

Then open this in your browser:

```text
http://localhost:8080
```

## Connect the frontend to the backend

At the top of the page there is a `Gateway node` field.

Use:

```text
http://127.0.0.1:8000
```

Then click `Refresh`.

After that you should be able to:

- upload `.txt` files
- see the node list
- delete files from the frontend

## If something is not working

If the frontend says the gateway is unreachable:

- make sure the backend node is still running
- make sure the URL in the gateway field matches the port you started
- refresh the page after restarting a node

If only one node shows up:

- check that all three backend terminals are running
- make sure each node was started with the correct `--peers` list

If you changed backend code and nothing updates:

- stop the backend processes with `Ctrl+C`
- start them again

## Running on another machine or over Wi-Fi

If you want someone else on the same network to open the app, replace `127.0.0.1` with your computer's local IP address.

Example:

```text
192.168.1.20
```

That means your backend commands would look more like:

```bash
python3 main.py --port 8000 --peers 192.168.1.20:8001 192.168.1.20:8002
```

And the frontend gateway would be:

```text
http://192.168.1.20:8000
```

## Stopping everything

In each terminal, press `Ctrl+C`.
