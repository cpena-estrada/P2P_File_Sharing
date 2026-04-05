# store.py

from pathlib import Path
import json
import time


"""
The intended strcture is:

storage/
├── node_5000/
│   ├── files/
│   │   ├── notes.txt
│   │   └── todo.txt
│   └── metadata/
│       ├── notes.txt.json
│       └── todo.txt.json
├── node_5001/
│   ├── files/
│   └── metadata/
└── ...
"""

class FileStore():
    def __init__(self, node_name: str):
        self.node_name = node_name
        self.base = Path('storage') / self.node_name

        # path objects to files and metadata directories for given node
        self.files_dir = self.base / 'files'
        self.metadata_dir = self.base / 'metadata'

        # actually make these directories
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)


    def write_file(self, file_name: str, text: str, timestamp: float = None):
        """
        Create file and its metadata

        Return timestamp so it can be used in the endpoint
        """
        if timestamp is None:
            timestamp = time.time()
        
        with open(self.files_dir / file_name, 'w') as f:
            f.write(text)

        # Write metadata as json
        data = {
            'filename': file_name,
            'timestamp': timestamp,
            'written_by': self.node_name
        }

        with open(self.metadata_dir / (file_name + '.json'), 'w') as f:
            json.dump(data, f, indent=2)
            # f.write(json.dumps(data, indent=2))

        return timestamp

    
    def read_file(self, file_name: str):
        """
        Read file and its metadata. 
        
        Return file text as string, metadata as dict
        """
        # Check files exist
        if not (self.files_dir / file_name).exists() or not (self.metadata_dir / (file_name + '.json')).exists():
            return None, None

        with open(self.files_dir / file_name, 'r') as f:
            text = f.read()

        with open(self.metadata_dir / (file_name + '.json'), 'r') as f:
            metadata = json.load(f)
            # metadata = json.loads(f.read())

        return text, metadata

    def delete_file(self, file_name: str):
        file_path = self.files_dir / file_name
        metadata_path = self.metadata_dir / (file_name + '.json')

        if not file_path.exists() or not metadata_path.exists():
            return False

        file_path.unlink()
        metadata_path.unlink()
        return True
    
    def list_files(self):
        files = {'files': []}
        for data in self.files_dir.iterdir():
            files['files'].append(data.name)

        return files

    def is_newer(self, file_name: str, incoming_timestamp):
        if not (self.files_dir / file_name).exists() or not (self.metadata_dir / (file_name + '.json')).exists():
            return True
        
        with open(self.metadata_dir / (file_name + '.json')) as f:
            metadata = json.load(f)

        if incoming_timestamp > metadata['timestamp']:
            return True
        
        return False
