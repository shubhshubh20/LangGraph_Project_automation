import json
import os
from pathlib import Path
import time
import requests
from demo_logger.json_logger import log_event
from core.state import ImageState, TransitionState

def safe_replace(src, dst, retries=5):
    for i in range(retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            time.sleep(0.1)
    raise

def create_transition_video_job(server_name: str,
                                staging_location: Path,  
                                character: str, 
                                transition_key: str,
                                start_image_state: ImageState,
                                end_image_state: ImageState,
                                transition_state: TransitionState) -> str:
    

    url = f"{server_name}/prompt"

    # with open("workflow_apis/transition_workflow_api.json", "r") as f:
    #     workflow = json.load(f)
    base_dir = Path(__file__).parent
    # file_path = base_dir / "test" / "transition_api.json"

    # with open(file_path, "r") as f:
    #     workflow_test = json.load(f)

    with open(base_dir / "workflow_apis" / "transition_workflow_api.json", "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # workflow_test["4"]["inputs"]["image"] = start_image_state["output_path"]
    # workflow_test["6"]["inputs"]["image"] = end_image_state["output_path"]
    # workflow_test["7"]["inputs"]["filename_prefix"] = f"{character}"

    total_time = end_image_state["time"] - start_image_state["time"]

    # TODO: update the workflow to get required inputs
    workflow["52"]["inputs"]["image"] = start_image_state["output_path"]
    workflow["72"]["inputs"]["image"] = end_image_state["output_path"]
    workflow["28"]["inputs"]["filename_prefix"] = character
    workflow["6"]["inputs"]["text"] = transition_state["prompt"]
    #get nearby integer to total_time * 16
    workflow["3"]["inputs"]["steps"] = round(total_time * 16)

    log_event("Persisting state to state.json")
    staging_location = staging_location / "test_workflow_api" / character / "transition"
    with open(staging_location / f'{character}_{transition_key}.tmp', 'w') as f:
        json.dump(workflow, f, indent=4)

    safe_replace(staging_location / f'{character}_{transition_key}.tmp', staging_location / f'{character}_{transition_key}.json')


    res = requests.post(url, json={"prompt": workflow}).json()
    job_id = res["prompt_id"]

    log_event(f"Creating transition job {transition_state['from_image']} to {transition_state['to_image']} with comfy ui")

    return job_id
