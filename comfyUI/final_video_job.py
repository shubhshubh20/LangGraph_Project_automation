import json
import os
from pathlib import Path
import time
import requests
# from demo_logger.json_logger import log_event
# from core.state import TransitionState
from state import TransitionState

def safe_replace(src, dst, retries=5):
    for i in range(retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            time.sleep(0.1)
    raise

def create_final_video_job(server_name: str, 
                           staging_location: Path,
                           character: str, 
                            transition_state_list: dict[str, TransitionState]) -> str:
    

    url = f"{server_name}/prompt"

    # with open("workflow_apis/video_combine_api.json", "r") as f:
    #     workflow = json.load(f)

    base_dir = Path(__file__).parent
    file_path = base_dir / "test" / "video_api.json"

    with open(file_path, "r") as f:
        workflow_test = json.load(f)

    with open(base_dir / "workflow_apis" / "video_combine_api.json", "r") as f:
        workflow = json.load(f)

    count = 0
    base_id = 100  # safer than 8 (avoid conflicts)

    workflow_test["9"]["inputs"]["inputcount"] = len(transition_state_list)
    workflow_test["7"]["inputs"]["filename_prefix"] = f'{character}'
    # Remove old LoadImage nodes (optional clean)
    for key in list(workflow_test.keys()):
        if workflow_test[key]["class_type"] == "VHS_LoadVideo":
            del workflow_test[key]

    for transition_key, transition_data in transition_state_list.items():

        node_id = str(base_id + count)

        workflow_test[node_id] = {
            "inputs": {
                "video": transition_data["output_path"],
                "force_rate": 0,
                "custom_width": 0,
                "custom_height": 0,
                "frame_load_cap": 0,
                "skip_first_frames": 0,
                "select_every_nth": 1,
                "format": "AnimateDiff"
                },
            "class_type": "VHS_LoadVideo",
            "_meta": {"title": "Load Video (Upload) 🎥🅥🅗🅢"}
        }

        workflow_test["9"]["inputs"][f"image_{count+1}"] = [node_id, 0]
        count = count + 1

    # total_vidoes = len(transition_state_list)

    with open(staging_location / "test_workflow_api" / f'{character}_final.tmp', 'w') as f:
        json.dump(workflow_test, f, indent=4)

    safe_replace(staging_location / "test_workflow_api" / f'{character}_final.tmp', staging_location / "test_workflow_api" / f'{character}_final.json')


    print("final workflow for video creation:")
    # print({"prompt": workflow_test})
    res = requests.post(url, json={"prompt": workflow_test}).json()
    print(res)
    job_id = res["prompt_id"]

    # log_event(f"Creating final complete video for {character} with comfy ui")

    return job_id
