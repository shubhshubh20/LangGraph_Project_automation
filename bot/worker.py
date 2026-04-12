import threading
import time
import json
from graph.flow import event_queue
from bot.telegram_bot import send_approval_request
from demo_logger.json_logger import log_event

def check_job_status(key: str, name: str):
    #randomly update the job status to completed, in_progress or failed for testing
    log_event(f"Checking job status for {name} with job id {key}...")


    #TODO: replace this with actual API call to comfy ui to check job status using prompt_id and update the state accordingly

    
    import random
    progress = random.choice(["in_progress", "completed", "failed"])
    # log_event(f"Checked job status for {job['type']} of character {job['character']}, new status: {job['status']}")
    if progress in ["completed"]:
        # send_telegram_request(job)
        event_queue.put({
            "type": "JOB_TELEGRAM_REQUEST_EVENT", 
            "payload": {
                "job_id": key
            }
        })
        send_approval_request(key, name)
        log_event("telegram request sent")
    if progress in ["failed"]:
        event_queue.put({
            "type": "JOB_FAILED_EVENT", 
            "payload": {
                "job_id": key
            }})


def should_terminate(state):

    #if any job is in progress return false
    for job in state.get("jobs", {}).values():
        if job["status"] == "in_progress":
            return False
        

    for char_data in state["characters"].values():
        for img in char_data.get("images", {}).values():
            status = img.get("status")

            if status in ["pending", "processing"]:
                return False

    # check if any transition is pending or processing
    for char_data in state["characters"].values():
        for transition in char_data.get("transitions", {}).values():
            status = transition.get("status")

            if status in ["pending", "processing"]:
                return False

    # check if final video is pending or processing
    for char_data in state["characters"].values():
        final_video_status = char_data.get("final_video", {}).get("status")

        if final_video_status in ["pending", "processing"]:
            return False
        
    return True


def poll_job_status(shutdown_event):

    log_event("Started polling thread to check job status every 10 seconds...")

    while True:
        time.sleep(2)

        log_event("Polling for job status updates...")
        # Get all pending jobs from the current state
        #read the current state from state.json and get all the jobs with status pending, then for each job check the status of the job using comfy ui api and if the job is done, update the state with output_path and status = done, then queue state update to create next job if any
        try:
            with open('state.json', 'r') as f:
                data = json.load(f)
                log_event("file found")
        except FileNotFoundError:
            log_event("state.json not found")
            continue

        if should_terminate(data):
            print("✅ All jobs completed. Signaling shutdown...")
            shutdown_event.set()
            break

        #get key and values of jobs
        for key in data.get("jobs", {}).keys():
            job = data["jobs"][key]
            if job["status"] == "in_progress":
                log_event("found in progress job, checking status...")
                #get image details from job and get expression and pose name from state using job details
                character_name = job["character"]
                if job["type"] == "image":
                    image_id = job["image_id"]
                    image_data = data["characters"][character_name]["images"][image_id]
                    check_job_status(key, f'Image of {character_name} with expression {image_data["expression"]} and pose {image_data["pose"]}  ')
                elif job["type"] == "transition":
                    transition_id = job["transition_id"]
                    transition_data = data["characters"][character_name]["transitions"][transition_id]
                    from_image = transition_data["from_image"]
                    to_image = transition_data["to_image"]
                    from_image_data = data["characters"][character_name]["images"][from_image]
                    to_image_data = data["characters"][character_name]["images"][to_image]
                    check_job_status(key, f'Transition video from {from_image_data["expression"]} and pose {from_image_data["pose"]} to {to_image_data["expression"]} and pose {to_image_data["pose"]} for character {character_name}')
                elif job["type"] == "final_video":
                    check_job_status(key, f'Final video for character {character_name}')

