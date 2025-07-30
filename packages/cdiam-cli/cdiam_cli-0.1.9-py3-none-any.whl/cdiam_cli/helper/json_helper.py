import json

def read(path: str):
    with open(path ,'r') as f:
        return json.load(f)
            
