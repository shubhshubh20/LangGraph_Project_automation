from core.state import RootState, Event, ImageState, CharacterState, FinalVideoState, TransitionState
import json

def get_input_json(event: Event) -> RootState:

    #read RootState id, and get id.json file to read the input data
    root_state_id = event["payload"]["episode_number"]
    data = {}
    state: RootState = {
        "id": root_state_id,
        "characters": {},
        "jobs": {},
        "event": event
    } 
 
    try:
        with open(f'{root_state_id}.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f'{root_state_id}.json not found')
        return state


    character_states = {}
    for char_key, char_data in data['characters'].items():
        # from data create ImageState first and then CharacterState and then RootState
        outfit = char_data["outfit"]
        posture = char_data["posture"]
        image_states = {}
        for img_key, img_data in char_data['images'].items():
            image_state: ImageState = {
                "index": img_data["index"],
                "expression_prompt": img_data["expression_prompt"],
                "expression": img_data["expression"],
                "pose_prompt": img_data["pose_prompt"],
                "pose": img_data["pose"],
                "from_time": img_data["from_time"],
                "to_time": img_data["to_time"],
                "status": "pending",
                "prompt_id": None,
                "output_path": None
            }
            image_states[img_key] = image_state

        #create transition states for adjacent images of each character 
        transition_states = {}
        images = char_data['images']
        sorted_images = sorted(images.items(), key=lambda x: x[1]['index'])
        for i in range(len(sorted_images) - 1):
            from_img_key, from_img_data = sorted_images[i]
            to_img_key, to_img_data = sorted_images[i + 1]
            transition_state: TransitionState = {
                "from_image": from_img_key,
                "to_image": to_img_key,
                "status": "pending",
                "prompt_id": None,
                "output_path": None
            }
            transition_states[f"{from_img_key}_to_{to_img_key}"] = transition_state
    
        #create final video state for each character
        final_video_state: FinalVideoState = {
            "status": "pending",
            "prompt_id": None,
            "output_path": None
        }

        character_state: CharacterState = {
            "outfit": outfit,
            "posture": posture,
            "images": image_states,
            "transitions": transition_states,
            "final_video": final_video_state
        }
        character_states[char_key] = character_state

    state["characters"] = character_states
    return state