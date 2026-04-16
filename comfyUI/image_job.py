import json
import os
from pathlib import Path
import time
import requests
from demo_logger.json_logger import log_event
from core.state import ImageState
    

def safe_replace(src, dst, retries=5):
    for i in range(retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            time.sleep(0.1)
    raise

def create_image_job(server_name:str, staging_location: Path, character: str, img_key: str, outfit: str, image_state: ImageState) -> str:

    # Here you would integrate with ComfyUI to create the image generation job
    url = f"{server_name}/prompt"

    character_ref_image_path = staging_location.parent / "ref" / f"{character}_{outfit}.png"  # This should be the actual path to the character reference image
    chai_cup_ref_image_path = staging_location.parent / "ref" / "chai_glass.png"
    final_prompt = ""
    char_def_prompt = ""

    final_prompt = f"{image_state['camera_angle']}. "\
        f"{image_state['pose_prompt']} and {image_state['expression_prompt']}. "\
            f"Keep the body proportions and facial features exactly the same. "\
            f"The background is a flat, solid chroma key green screen (#00FF00)."
        # char_def_prompt = "Young Indian man, early 20s, calm observant personality, medium-length casual haircut with soft layers, \
        #     hair slightly longer on top and sides, some hair falling naturally toward the forehead, relaxed natural hairstyle, no glasses, \
        #         flat relaxed eyebrows, calm observant eyes with neutral expression, subtle polite smile, emotionally unreadable face, \
        #             slightly slouched relaxed posture, blends easily into the group, looks normal and approachable\
        #                 \nRules:\nNO glasses \nHair may touch forehead \nNo visible stress or sweat \nMust look boringly normal"
        

    # TODO: update the chai glass image in the required tab.
    # with open("workflow_apis/character_creator_api.json", "r") as f:
    #     workflow = json.load(f)
    
    base_dir = Path(__file__).parent
    # file_path = base_dir / "test" / "image_api.json"
    # print(file_path.__str__())
    # with open(file_path, "r") as f:
    #     test_workflow = json.load(f)

    with open(base_dir / "workflow_apis" / "character_creator_api.json", "r") as f:
        workflow = json.load(f)
    
    # print(test_workflow)

    # test_workflow["4"]["inputs"]["image"] = f'{image_state["output_path"]}'
    # test_workflow["10"]["inputs"]["filename_prefix"] = f'{character}'

    workflow["213"]["inputs"]["image"] = character_ref_image_path.__str__()
    # workflow["515"]["inputs"]["string"] = char_def_prompt
    workflow["592"]["inputs"]["string"] = final_prompt
    workflow["368"]["inputs"]["filename_prefix"] = f'{character}'
    workflow["1446"]["inputs"]["image"] = chai_cup_ref_image_path.__str__()

    log_event("Persisting state to state.json")
    staging_location = staging_location / "test_workflow_api" / character / "image"
    with open(staging_location / f'{character}_{img_key}.tmp', 'w') as f:
        json.dump(workflow, f, indent=4)

    safe_replace(staging_location / f'{character}_{img_key}.tmp', staging_location / f'{character}_{img_key}.json')

    res = requests.post(url, json={"prompt": workflow}).json()
    # print(res)
    job_id = res["prompt_id"]

    log_event(f"Creating image job {img_key} with comfy ui")

    return job_id