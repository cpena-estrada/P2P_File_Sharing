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
    def __init__(self, node_name):
        self.base = Path('storage') / node_name

        # path objects to files and metadata directories for given node
        self.files_dir = self.base / 'files'
        self.metadata_dir = self.base / 'metadata'

        # actually make these directories
        self.files_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)


    def write_file(self, file_name: str, text: str):
        """
        Create file and its metadata
        """
        with open(self.files_dir / file_name, 'w') as f:
            f.write(text)

        # Write metadata as json
        data = {
            'filename': file_name,
            'timestamp': time.time()
        }

        with open(self.metadata_dir / (file_name + '.json'), 'w') as f:
            json.dump(data, f, indent=2)
            # f.write(json.dumps(data, indent=2))

    
    def read_file(self, file_name: str):
        """
        Read file and its metadata. 
        
        Return file text as string, metadata as dict
        """

        # Check files exist
        if not self.files_dir.exists() or not self.metadata_dir.exists():
            return None, None

        with open(self.files_dir / file_name, 'r') as f:
            text = f.read()

        with open(self.metadata_dir / (file_name + '.json'), 'r') as f:
            metadata = json.load(f)
            # metadata = json.loads(f.read())

        return text, metadata
    

    def is_newer(self, file_name: str, timestamp):
        
        if not (self.files_dir / file_name).exists() or not (self.metadata_dir / (file_name + '.json')).exists():
            return True
        
        with open(self.metadata_dir / (file_name + '.json')) as f:
            metadata = json.load(f)

        if timestamp > metadata['timestamp']:
            return True
        
        return False

             