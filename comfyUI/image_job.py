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

    if character == "Arjun":
        final_prompt = f"{image_state['camera_angle']} view anime illustration of the man from the reference image, \
            {image_state['pose_prompt']} and {image_state['expression_prompt']}. He is interacting with the steaming cutting chai glass \
                from the second reference image as described. The background is a flat,\
                    solid chroma key green screen (#00FF00)."
        char_def_prompt = "Young Indian man, early 20s, calm observant personality, medium-length casual haircut with soft layers, \
            hair slightly longer on top and sides, some hair falling naturally toward the forehead, relaxed natural hairstyle, no glasses, \
                flat relaxed eyebrows, calm observant eyes with neutral expression, subtle polite smile, emotionally unreadable face, \
                    slightly slouched relaxed posture, blends easily into the group, looks normal and approachable\
                        \nRules:\nNO glasses \nHair may touch forehead \nNo visible stress or sweat \nMust look boringly normal"
        
    elif character == "Tara":
        final_prompt = f"{image_state['camera_angle']} view anime illustration of the woman from the reference image, \
            {image_state['pose_prompt']} and {image_state['expression_prompt']}. She is interacting with the steaming \
                cutting chai glass from the second reference image as described. \
                    The background is a flat, solid chroma key green screen (#00FF00)."
        char_def_prompt = "Young Indian woman, early 20s, energetic and optimistic personality, wide expressive eyes, big friendly smile, \
            animated facial expression, leaning forward body language, loose or messy half-ponytail hairstyle, dark brown hair with subtle warm highlights, \
                slightly uneven and wild look, spontaneous and lively vibe \
                \nRules: \nHair should look slightly messy \nExpression can change a lot \nNever perfectly neat"

    elif character == "Naina":
        final_prompt = f"{image_state['camera_angle']} view anime illustration of the woman from the reference image, \
            sitting on a red plastic stool, {image_state['pose_prompt']} and {image_state['expression_prompt']}. \
                She is interacting with the steaming cutting chai glass from the second reference image as described. \
            The background is a flat, solid chroma key green screen (#00FF00)."
        char_def_prompt = "Young Indian woman, early 20s, soft dreamy personality, gentle eyes, subtle smile, often looking slightly away or upward, \
            relaxed posture, artistic and poetic vibe, calm and introspective \
            \nRules: \nAvoid sharp angles \nEverything should feel soft"

    elif character == "Aditya":
        final_prompt = f"{image_state['camera_angle']} view anime illustration of the man from the reference image, \
            {image_state['pose_prompt']} and {image_state['expression_prompt']}. He is interacting with the steaming cutting \
                chai glass from the second reference image as described. \
            The background is a flat, solid chroma key green screen (#00FF00)."
        char_def_prompt = "Young Indian man, early 20s, anxious overthinking personality, short neatly combed hair with a visible forehead, \
            classic side-part haircut, hair length above ears and not covering forehead, thin rectangular glasses, eyebrows angled inward and slightly raised, \
                worried alert eyes, subtle eye strain visible, tense facial muscles, slight sweat drop on temple, mouth mid-sentence, expressive hand gestures as if \
                    explaining urgently, upright but tense posture, looks mentally overloaded and emotionally pressured\
                    \nRules:\nNO long hair \nNO fringe covering forehead \nGlasses are mandatory \nFace must show stress, not calm"

    elif character == "Ananya":
        final_prompt = f"{image_state['camera_angle']} view anime illustration of the woman from the reference image, \
            sitting on a white wooden stool, {image_state['pose_prompt']} and {image_state['expression_prompt']}. \
                She is interacting with the steaming cutting chai glass from the second reference image as described. \
            The background is a flat, solid chroma key green screen (#00FF00)."
        char_def_prompt = "Young Indian woman, early 20s, confident and dominant personality, sharp expressive eyes, slightly raised eyebrows, \
            confident half-smile, upright posture, hands on hips or pointing, neat hair, modern urban look, looks decisive and in control \
                  \n Rules: \nNever loose hair \nNever playful expression \nAlways looks like she’s leading"

    # TODO: update the chai glass image in the required tab.
    # with open("workflow_apis/character_creator_api.json", "r") as f:
    #     workflow = json.load(f)
    
    base_dir = Path(__file__).parent
    file_path = base_dir / "test" / "image_api.json"
    # print(file_path.__str__())
    with open(file_path, "r") as f:
        test_workflow = json.load(f)

    with open(base_dir / "workflow_apis" / "character_creator_api.json", "r") as f:
        workflow = json.load(f)
    
    # print(test_workflow)

    test_workflow["4"]["inputs"]["image"] = f'{image_state["output_path"]}'
    test_workflow["10"]["inputs"]["filename_prefix"] = f'{character}'

    workflow["213"]["inputs"]["image"] = character_ref_image_path.__str__()
    workflow["515"]["inputs"]["string"] = char_def_prompt
    workflow["588"]["inputs"]["value"] = character
    workflow["592"]["inputs"]["string"] = final_prompt
    workflow["368"]["inputs"]["filename_prefix"] = f'{character}'
    workflow["1446"]["inputs"]["image"] = chai_cup_ref_image_path.__str__()

    log_event("Persisting state to state.json")
    with open(staging_location / "test_workflow_api" / f'{character}_{img_key}.tmp', 'w') as f:
        json.dump(workflow, f, indent=4)

    safe_replace(staging_location / "test_workflow_api" / f'{character}_{img_key}.tmp', staging_location / "test_workflow_api" / f'{character}_{img_key}.json')

    res = requests.post(url, json={"prompt": test_workflow}).json()
    # print(res)
    job_id = res["prompt_id"]

    log_event(f"Creating image job {img_key} with comfy ui")

    return job_id