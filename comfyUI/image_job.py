import json
import requests
from main import server_name
from demo_logger.json_logger import log_event
from ..core.state import ImageState

def create_image_job(character: str, outfit: str, posture: str, image_state: ImageState) -> str:

    # Here you would integrate with ComfyUI to create the image generation job
    url = f"{server_name}/prompt"
    character_ref_image_path = f"/path/to/ref/img/folder/{character}/{outfit}.png"  # This should be the actual path to the character reference image
    with open("workflow_apis/character_creator_api.json", "r") as f:
        workflow = json.load(f)
    


    workflow["213"]["inputs"]["images"] = character_ref_image_path
    workflow["515"]["inputs"]["string"] = f'Here character definition / rules prompt should be added, this will be always fixed'
    workflow["588"]["inputs"]["value"] = character
    workflow["592"]["inputs"]["string"] = f'Here expression prompt should be added, {posture}{image_state["expression_prompt"]}{image_state["pose_prompt"]}'
    workflow["368"]["inputs"]["filename_prefix"] = f'{image_state["output_path"]}'

    res = requests.post(url, json={"prompt": workflow}).json()
    job_id = res["job_id"]

    log_event("Creating image job with comfy ui")

    return job_id