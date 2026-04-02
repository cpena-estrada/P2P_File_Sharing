# routes.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from store import FileStore


app = FastAPI()


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
    store.write_file(file_name, body.text)
    return {
        'status': 'ok',
        'file_name': file_name
    }
    

@app.post('/sync/{file_name}')
def sync_file(file_name: str, body: FileSync):
    """
    Overwrite file for the given node if incoming timestamp is greater than local timestamp
    """
    if store.is_newer(file_name, body.incoming_timestamp):
        store.write_file(file_name, body.text, body.incoming_timestamp)
        return {'status': 'accepted', 'file_name': file_name}
    
    return {'status': 'rejected', 'file_name': file_name}