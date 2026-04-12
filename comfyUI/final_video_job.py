import json
import requests
from main import server_name
from demo_logger.json_logger import log_event
from ..core.state import TransitionState

def create_final_video_job(character: str, 
                            transition_state_list: dict[str, TransitionState]) -> str:
    

    url = f"{server_name}/prompt"

    with open("workflow_apis/video_combine_api.json", "r") as f:
        workflow = json.load(f)

    # TODO: update the workflow to get required inputs

    total_vidoes = len(transition_state_list)

    #TODO: dynamically change the workflow json file to get multiple inputs from the system

    # Following code is directly used from chatgpt change that in order to get proper workflow

    # import json

    # files = [
    #     "naina_transition_1.webp",
    #     "naina_transition_2.webp",
    #     "naina_transition_3.webp",
    #     "naina_transition_4.webp"
    # ]

    # with open("video_combine_api.json") as f:
    #     workflow = json.load(f)["prompt"]

    # # Clear old images
    # workflow["7"]["inputs"] = {"inputcount": len(files)}

    # # Remove old LoadImage nodes (optional clean)
    # for key in list(workflow.keys()):
    #     if workflow[key]["class_type"] == "LoadImage":
    #         del workflow[key]

    # # Add new nodes
    # base_id = 100  # safer than 8 (avoid conflicts)

    # for i, file in enumerate(files):
    #     node_id = str(base_id + i)

    #     workflow[node_id] = {
    #         "inputs": {"image": file},
    #         "class_type": "LoadImage",
    #         "_meta": {"title": "Load Image"}
    #     }

    #     workflow["7"]["inputs"][f"image_{i+1}"] = [node_id, 0]


    res = requests.post(url, json={"prompt": workflow}).json()
    job_id = res["job_id"]

    log_event(f"Creating final complete video for {character} with comfy ui")

    return job_id
