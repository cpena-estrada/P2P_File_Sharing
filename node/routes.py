# routes.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from store import FileStore
from network import replicate, replicate_delete
import network


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Models
class FileIn(BaseModel):
    text: str

class FileSync(BaseModel):
    text: str
    incoming_timestamp: float
    written_by: str


store: FileStore = None  # gets set by main.py at startup


@app.get('/health')
def health():
    return {
        'status': 'ok',
        'message': f'hi from: {store.node_name}'
    }


@app.get('/cluster')
def cluster(request: Request):
    current_address = f'{request.url.hostname}:{request.url.port}'
    known_peers = sorted(set(network.peers))
    online_peers = sorted(set(network.online_peers))

    nodes = [{
        'name': store.node_name,
        'address': current_address,
        'online': True,
        'role': 'self'
    }]

    for peer in known_peers:
        nodes.append({
            'name': f"node_{peer.split(':')[-1]}",
            'address': peer,
            'online': peer in online_peers,
            'role': 'peer'
        })

    return {
        'current_node': store.node_name,
        'current_address': current_address,
        'peers': known_peers,
        'online_peers': online_peers,
        'nodes': nodes
    }


@app.get('/files')
def list_files():
    return store.list_files()
    

@app.get('/files/{file_name}')
def get_file(file_name: str):
    text, metadata = store.read_file(file_name)

    if text is None:
        raise HTTPException(status_code=404, detail="file not found")
    
    return {
        'text': text,
        'metadata': metadata
    }


@app.post('/files/{file_name}')
def write_file(file_name: str, body: FileIn):
    timestamp = store.write_file(file_name, body.text)
    # Replicate this write across nodes
    replicate(file_name, body.text, timestamp, store.node_name)
    
    return {
        'status': 'ok',
        'file_name': file_name
    }


@app.delete('/files/{file_name}')
def delete_file(file_name: str):
    deleted = store.delete_file(file_name)

    if not deleted:
        raise HTTPException(status_code=404, detail='file not found')

    replicate_delete(file_name)

    return {
        'status': 'ok',
        'file_name': file_name
    }
    

@app.post('/sync/{file_name}')
def sync_file(file_name: str, body: FileSync):
    """
    On the receiver side, overwrite file for the a node if incoming timestamp is greater than local timestamp

    Called by replicate()
    """
    if store.is_newer(file_name, body.incoming_timestamp):
        store.write_file(file_name, body.text, body.incoming_timestamp)
        return {'status': 'accepted', 'file_name': file_name}
    
    return {'status': 'rejected', 'file_name': file_name}


@app.delete('/sync/{file_name}')
def sync_delete_file(file_name: str):
    deleted = store.delete_file(file_name)

    if deleted:
        return {'status': 'accepted', 'file_name': file_name}

    return {'status': 'missing', 'file_name': file_name}
