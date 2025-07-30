
import json, os
MEMORY_PATH = "/tmp/memory.json"

def save_memory(entry):
    data = []
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, 'r') as f:
            data = json.load(f)
    data.append(entry)
    with open(MEMORY_PATH, 'w') as f:
        json.dump(data[-100:], f, indent=2)

def recall_memory(keywords):
    if not os.path.exists(MEMORY_PATH):
        return []
    with open(MEMORY_PATH, 'r') as f:
        data = json.load(f)
    return [e for e in data if any(k.lower() in str(e).lower() for k in keywords)]
