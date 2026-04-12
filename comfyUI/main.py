import requests
import json

# Load your exported workflow
with open("controlnet_preprocessor.json", "r") as f:
    workflow = json.load(f)

print(workflow)
url = "http://localhost:8188/prompt"

res = requests.post(url, json=workflow)
print(res.json())