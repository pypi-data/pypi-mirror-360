import os
import json
from pathlib import Path

file_path = Path.home() / "api_hunt_envs" / "custom_pattern.json"

file_path.parent.mkdir(parents=True, exist_ok=True)

if file_path.parent.exists():
    FILE_PATH = file_path
else:
    FILE_PATH = f"{Path.home()}/custom_pattern.json"

def display():
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size <= 2:
        
        print("File is empty or not found")
        return
    
    with open(FILE_PATH,"r") as file:
        data = json.load(file)

    for d in data:
        print(f"key_name: {d['key_name']}, pattern: {d['pattern']}")

def delete_data_from_custom(key_name):

    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size <= 2:
        
        print("File is empty or not found")
        return
    with open(FILE_PATH,'r') as file:
        data = json.load(file)

    deleted = False
    for i in range(len(data)-1,-1,-1):
        if key_name.lower() in data[i].get("key_name","").lower():
            del data[i]
            deleted = True

    if deleted: 
        with open(FILE_PATH,"w") as file:
            json.dump(data,file,indent=4)
        print(f"deleted key {key_name}")
        return
    else:
        print("key not found")
        return


def add_data_to_custom(key:str,pattern:str):

    if not key and not pattern:
        print("No Key and Pattern provided as input")
        return
    
    if not os.path.exists(FILE_PATH) or os.stat(FILE_PATH).st_size == 0:
        with open(FILE_PATH, 'w') as f:
            json.dump([], f)

    data = {"key_name":key,"pattern":pattern}

    with open(FILE_PATH,"r") as file:
        content = json.load(file)

    content.append(data)

    with open(FILE_PATH,"w") as file:
        json.dump(content,file,indent=4)
    print(f"data added to file {data}")