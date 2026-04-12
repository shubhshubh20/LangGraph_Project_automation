import json
import requests
from main import server_name
from demo_logger.json_logger import log_event
from ..core.state import ImageState, TransitionState

def create_transition_video_job(character: str, 
                                start_image_state: ImageState,
                                end_image_state: ImageState,
                                transition_state: TransitionState) -> str:
    

    url = f"{server_name}/prompt"

    with open("workflow_apis/transition_workflow_api.json", "r") as f:
        workflow = json.load(f)

    # TODO: update the workflow to get required inputs

    res = requests.post(url, json={"prompt": workflow}).json()
    job_id = res["job_id"]

    log_event("Creating image job with comfy ui")

    return job_id
