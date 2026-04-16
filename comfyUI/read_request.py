import requests
import json

# print(workflow)
prompt_id = "1d300bfe-1d83-446b-88aa-477b01a2cec9"
url = f'http://localhost:8188/history/{prompt_id}'

res = requests.get(url).json()
status = res[prompt_id]["status"]["status_str"]

print(status)