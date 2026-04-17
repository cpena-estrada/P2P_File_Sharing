```markdown
# P2P File Sharing

A serverless peer-to-peer file sharing system where every node runs identical code and participates equally — no central server required. Files written to any node are automatically replicated across the cluster, conflicts are resolved via Last-Write-Wins timestamps, and nodes detect each other's availability through a heartbeat system.

## How It Works

- **Replication** — every write is immediately pushed to all online peers so every node holds a full copy of every file
- **Eventual Consistency** — nodes don't block on global agreement; they converge once the network reconnects
- **Last-Write-Wins (LWW)** — every write records a Unix timestamp; `is_newer()` ensures the most recent version always wins
- **Heartbeat Fault Detection** — a background thread pings every peer's `/health` endpoint every 10 seconds to track who's online

## Project Structure

```
P2P_File_Sharing/
├── node/
│   ├── main.py       # Entry point — starts a node on a given port with a list of peers
│   ├── store.py      # FileStore class — handles local file reads, writes, deletes, and LWW checks
│   ├── network.py    # Replication, heartbeat loop, and startup sync
│   └── routes.py     # FastAPI app — exposes all HTTP endpoints
├── frontend/
│   ├── index.html    # Upload UI and node status panel
│   ├── app.js
│   └── styles.css
└── requirements.txt
```

## Requirements

- Python 3.8+
- pip

## Setup

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Cluster

Each node is started with its own port and a list of peer addresses. Open three terminals and run one command in each:

**Terminal 1**
```bash
source .venv/bin/activate
cd node
python3 main.py --port 8000 --peers 127.0.0.1:8001 127.0.0.1:8002
```

**Terminal 2**
```bash
source .venv/activate
cd node
python3 main.py --port 8001 --peers 127.0.0.1:8000 127.0.0.1:8002
```

**Terminal 3**
```bash
source .venv/bin/activate
cd node
python3 main.py --port 8002 --peers 127.0.0.1:8000 127.0.0.1:8001
```

Each terminal should show Uvicorn startup logs confirming the node is running.

## Running the Frontend

Open a fourth terminal:

```bash
cd frontend
python3 -m http.server 8080
```

Then open `http://localhost:8080` in your browser. In the **Gateway node** field at the top, enter:

```
http://127.0.0.1:8000
```

Click **Refresh**. You should now be able to upload `.txt` files, view the node list, and see files replicate across the cluster.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Liveness probe used by the heartbeat system |
| `GET` | `/files` | List all files on this node |
| `GET` | `/files/<name>` | Read a file and its metadata |
| `POST` | `/files/<name>` | Write a file and replicate to all online peers |
| `DELETE` | `/files/<name>` | Delete a file and replicate the deletion |
| `GET` | `/cluster` | View all known peers and their online/offline status |
| `POST` | `/sync/<name>` | Internal — peer-facing sync receiver (LWW check applied) |
| `DELETE` | `/sync/<name>` | Internal — peer-facing deletion receiver |

## Running Across Multiple Machines

Replace `127.0.0.1` with your machine's local IP address. For example, if your IP is `192.168.1.20`:

```bash
python3 main.py --port 8000 --peers 192.168.1.20:8001 192.168.1.20:8002
```

And point the frontend gateway at:

```
http://192.168.1.20:8000
```

## Troubleshooting

**Frontend says gateway is unreachable** — confirm the backend node is still running and the URL in the gateway field matches the port you started.

**Only one node shows up** — check that all three terminals are running and each was started with the correct `--peers` list.

**Changes to backend code aren't reflected** — stop all nodes with `Ctrl+C` and restart them.

## Dependencies

```
fastapi>=0.110.0
uvicorn>=0.29.0
requests>=2.31.0
```
```
