import requests
import json

# Load your exported workflow
# with open("controlnet_preprocessor.json", "r") as f:
#     workflow = json.load(f)

# print(workflow)
# url = "http://localhost:8188/prompt"

# res = requests.post(url, json=workflow)
# print(res.json())

from pathlib import Path
import json

from final_video_job import create_final_video_job


server_name = "http://localhost:8188"
staging_location = Path("D:\\youtube\\corner_table\\LangGraph_Project_automation\\comfyUI\\staging_loc\\s01_e09")

transitions = {
                "image_1_to_image_2": {
                    "from_image": "image_1",
                    "to_image": "image_2",
                    "prompt": "same woman, consistent character, sitting, turning head to a profile view, bringing the glass tea cup up from her lap to her mouth to take a slow sip with her right hand, stable hands, cinematic stillness, smooth controlled motion",
                    "status": "approved",
                    "prompt_id": "52adf8c3-3466-4e68-a162-4bbe7e467dea",
                    "output_path": "D:\\youtube\\corner_table\\LangGraph_Project_automation\\comfyUI\\staging_loc\\s01_e09\\Ananya\\image_1_to_image_2.webp"
                },
                "image_2_to_image_3": {
                    "from_image": "image_2",
                    "to_image": "image_3",
                    "prompt": "same woman, consistent character, sitting, turning head forward and tilting it slightly, lowering the glass tea cup back to her lap and holding it with both hands, stable hands, cinematic stillness, smooth controlled motion",
                    "status": "approved",
                    "prompt_id": "596e58be-12ae-44f1-8f3f-c568ce894697",
                    "output_path": "D:\\youtube\\corner_table\\LangGraph_Project_automation\\comfyUI\\staging_loc\\s01_e09\\Ananya\\image_2_to_image_3.webp"
                },
                "image_3_to_image_4": {
                    "from_image": "image_3",
                    "to_image": "image_4",
                    "prompt": "same woman, consistent character, sitting, turning head to a profile view and looking down slightly, shifting weight, releasing her right hand to hold the glass tea cup in her left hand, stable hands, cinematic stillness, smooth controlled motion",
                    "status": "approved",
                    "prompt_id": "4019eb3d-36c9-4e19-8c61-f4735d38831e",
                    "output_path": "D:\\youtube\\corner_table\\LangGraph_Project_automation\\comfyUI\\staging_loc\\s01_e09\\Ananya\\image_3_to_image_4.webp"
                },
                "image_4_to_image_5": {
                    "from_image": "image_4",
                    "to_image": "image_5",
                    "prompt": "same woman, consistent character, sitting, turning head forward, nodding slowly in agreement, holding the glass tea cup steady in her left hand on her lap, stable hands, cinematic stillness, smooth controlled motion",
                    "status": "approved",
                    "prompt_id": "814c5a4e-24de-4e37-aecc-21e6230c131b",
                    "output_path": "D:\\youtube\\corner_table\\LangGraph_Project_automation\\comfyUI\\staging_loc\\s01_e09\\Ananya\\image_4_to_image_5.webp"
                },
                "image_5_to_image_6": {
                    "from_image": "image_5",
                    "to_image": "image_6",
                    "prompt": "same woman, consistent character, sitting, suddenly snapping head to a profile view, straightening posture upward in surprise, holding the glass tea cup steady in her left hand, stable hands, cinematic stillness, fast controlled motion",
                    "status": "approved",
                    "prompt_id": "6e815b5d-394b-4cd8-811e-604488d06faa",
                    "output_path": "D:\\youtube\\corner_table\\LangGraph_Project_automation\\comfyUI\\staging_loc\\s01_e09\\Ananya\\image_5_to_image_6.webp"
                },
                "image_6_to_image_7": {
                    "from_image": "image_6",
                    "to_image": "image_7",
                    "prompt": "same woman, consistent character, sitting, relaxing into a bright amused smile, turning head forward, bringing the glass tea cup up from her lap to take a sip with her left hand, stable hands, cinematic stillness, smooth controlled motion",
                    "status": "approved",
                    "prompt_id": "f5842bc0-1dec-4bb9-ab9f-6d1d03e60267",
                    "output_path": "D:\\youtube\\corner_table\\LangGraph_Project_automation\\comfyUI\\staging_loc\\s01_e09\\Ananya\\image_6_to_image_7.webp"
                }
            }

job_id = create_final_video_job(server_name, staging_location,"Ananya", transitions)


base_dir = Path(__file__).parent
file_path = base_dir / "test" / "transition_api.json"

with open(file_path, "r") as f:
    workflow_test = json.load(f)

print(workflow_test)