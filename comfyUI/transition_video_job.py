import json
from pathlib import Path
import requests
from demo_logger.json_logger import log_event
from core.state import ImageState, TransitionState

def create_transition_video_job(server_name: str, 
                                character: str, 
                                start_image_state: ImageState,
                                end_image_state: ImageState,
                                transition_state: TransitionState) -> str:
    

    url = f"{server_name}/prompt"

    # with open("workflow_apis/transition_workflow_api.json", "r") as f:
    #     workflow = json.load(f)
    base_dir = Path(__file__).parent
    file_path = base_dir / "test" / "transition_api.json"

    with open(file_path, "r") as f:
        workflow_test = json.load(f)

    workflow_test["4"]["inputs"]["image"] = start_image_state["output_path"]
    workflow_test["6"]["inputs"]["image"] = end_image_state["output_path"]
    workflow_test["7"]["inputs"]["filename_prefix"] = f"{character}"


    # TODO: update the workflow to get required inputs

    res = requests.post(url, json={"prompt": workflow_test}).json()
    job_id = res["prompt_id"]

    log_event("Creating image job with comfy ui")

    return job_id
