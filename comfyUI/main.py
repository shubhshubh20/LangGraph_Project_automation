import requests
import json

# Load your exported workflow
# with open("controlnet_preprocessor.json", "r") as f:
#     workflow = json.load(f)

# print(workflow)
# url = "http://localhost:8188/prompt"

# res = requests.post(url, json=workflow)
# print(res.json())

from pathlib import Path
import json

base_dir = Path(__file__).parent
file_path = base_dir / "test" / "transition_api.json"

with open(file_path, "r") as f:
    workflow_test = json.load(f)

print(workflow_test)