# Frontend

This folder contains a very simple standalone frontend for the P2P file sharing
project.

## What it shows

- A client upload panel for `.txt` files
- A small list of connected nodes
- A replication demo where uploaded text appears on every node card

## How to run

Open [index.html](./index.html) directly in a browser.

If you want to serve it locally instead:

```bash
cd frontend
python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Notes

This frontend now talks to a running backend node.

Start one or more nodes first, then open the frontend and point the "Gateway
node" field at one of them.

Example:

```bash
cd node
python3 main.py --port 8000 --peers 127.0.0.1:8001 127.0.0.1:8002
python3 main.py --port 8001 --peers 127.0.0.1:8000 127.0.0.1:8002
python3 main.py --port 8002 --peers 127.0.0.1:8000 127.0.0.1:8001
```
