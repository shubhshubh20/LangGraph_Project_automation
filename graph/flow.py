from pathlib import Path
from queue import Queue
from typing import Callable, cast
import time

from prompt_toolkit import prompt
from core.state import ImageState, RootState
import json
import uuid
import os
from core.events import get_input_json
from langgraph.graph import StateGraph, START, END
from IPython.display import Image, display
from comfyUI.image_job import create_image_job
from comfyUI.transition_video_job import create_transition_video_job
from comfyUI.final_video_job import create_final_video_job
from demo_logger.json_logger import log_event


def safe_replace(src, dst, retries=5):
    for i in range(retries):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            time.sleep(0.1)
    raise

def persist_state(state: RootState) -> RootState:

    log_event("Persisting state to state.json")
    with open('state.tmp', 'w') as f:
        json.dump(state, f, indent=4)

    safe_replace('state.tmp', 'state.json')

    return state


event_queue = Queue()

def update_state(state: RootState) -> RootState:

    
    new_state: RootState
    event = state["event"]

    log_event("Updating state with event", event=event)

    if event and event["type"] == "INITIALIZE":
        ##making sure that telegram bot is up and running before we initialize the state, 
        # so that we can send the approval/rejection messages to telegram without any issues.
        log_event("Waiting for Telegram bot to start before initializing state...")
        time.sleep(5)  
        # 
        # 
        try:
            with open('state.json', 'r') as f:
                data = json.load(f)
            new_state = cast(RootState, data)
            log_event("state.json already exists, loading state...")
        except FileNotFoundError: 
            log_event("Initializing state with input JSON...")
            new_state = get_input_json(event)
            log_event("State initialized.")

    else:
        with open('state.json', 'r') as f:
            data = json.load(f)
        new_state = cast(RootState, data)


        if event and event["type"] == "JOB_TELEGRAM_REQUEST_EVENT":
            job = new_state["jobs"][event["payload"]["job_id"]]
            if job:
                job["status"] = "sent_for_approval"
            log_event(f"Telegram approval request sent for job {event['payload']['job_id']}")

        elif event and event["type"] == "JOB_FAILED_EVENT":
            job = new_state["jobs"][event["payload"]["job_id"]]
            if job:
                job["status"] = "failed"
                if job["type"] == "image":
                    new_state["characters"][job["character"]]["images"][job["image_id"]]["status"] = "pending"
                elif job["type"] == "transition":
                    new_state["characters"][job["character"]]["transitions"][job["transition_id"]]["status"] = "pending"
                elif job["type"] == "final_video":
                    new_state["characters"][job["character"]]["final_video"]["status"] = "pending"
        
        elif event and event["type"] == "TELEGRAM_APPROVE_EVENT":
            job = new_state["jobs"][event["payload"]["job_id"]]
            if job:
                job["status"] = "completed"
                if job["type"] == "image":
                    new_state["characters"][job["character"]]["images"][job["image_id"]]["status"] = "approved"
                elif job["type"] == "transition":
                    new_state["characters"][job["character"]]["transitions"][job["transition_id"]]["status"] = "approved"
                elif job["type"] == "final_video":
                    new_state["characters"][job["character"]]["final_video"]["status"] = "approved"
            log_event(f"Received Telegram approval for job {event['payload']['job_id']}")

            
        elif event and event["type"] == "TELEGRAM_REJECT_EVENT":
            job = new_state["jobs"][event["payload"]["job_id"]]
            if job:
                job["status"] = "completed"
                if job["type"] == "image":
                    new_state["characters"][job["character"]]["images"][job["image_id"]]["status"] = "rejected"
                elif job["type"] == "transition":
                    new_state["characters"][job["character"]]["transitions"][job["transition_id"]]["status"] = "rejected"
                elif job["type"] == "final_video":
                    new_state["characters"][job["character"]]["final_video"]["status"] = "rejected"
            log_event(f"Received Telegram rejection for job {event['payload']['job_id']}")

    return new_state


def state_worker():
    graph = initiate_graph()
    
    while True:
        event = event_queue.get()

        log_event("Event Enqueued", event=event)
        
        state: RootState = {
            "id": "",
            "server_name": "",
            "staging_location": "",
            "characters": {},
            "jobs": {},
            "event": event
        }

        log_event("graph invoked")
        # state = update_state(state)
        graph.invoke(state)

        event_queue.task_done()


def create_next_job(state: RootState) -> RootState:
    # Placeholder for the actual job creation logic
    # Example: return JobState(type="image", character="char1", image_id="img1", transition_id=None, status="pending")
    #if all the images and videos are approved including final video, then terminate the workflow

    # job_id = uuid.uuid4().hex
    
    #if any image is pending, create an image job
    server_name = state["server_name"]
    staging_location = Path(state["staging_location"])
    if state["characters"]:
        for char_key, char_data in state["characters"].items():
            character_staging_loc = staging_location / char_key
            character_staging_loc.mkdir(parents=True, exist_ok=True)
            outfit = char_data["outfit"]
            posture = char_data["posture"]
            for img_key, img_data in char_data["images"].items():
                if img_data["status"] == "pending" or img_data["status"] == "rejected":
                    # TODO: decide on the final output path stucture for the image
                    output_path = f'{(character_staging_loc / img_key).__str__()}.png'
                    img_data["output_path"] = output_path

                    job_id = create_image_job(
                        server_name, 
                        char_key,
                        img_key,
                        outfit,
                        posture,
                        img_data
                    )

                    state["jobs"][job_id] = {
                        "type": "image",
                        "character": char_key,
                        "image_id": img_key,
                        "transition_id": "",
                        "status": "in_progress",
                        "output_path": output_path
                    }
                    img_data["status"] = "processing"
                    img_data["prompt_id"] = job_id
                    log_event("Image Job created, updating state...")

                    # event_queue.put({
                    #     "type": "NEW_IMAGE_JOB", 
                    #     "payload": {
                    #         "character": char_key,
                    #         "image_key": img_key
                    #         }
                    #     })
                    return state
                    # return f"Image job"

    #else if any transition is pending, create a transition job condition if adjacent images are approved, then create a transition job
    if state["characters"]:
        for char_key, char_data in state["characters"].items():
            character_staging_loc = staging_location / char_key
            character_staging_loc.mkdir(parents=True, exist_ok=True)
            outfit = char_data["outfit"]
            posture = char_data["posture"]
            for transition_key, transition_data in char_data["transitions"].items():
                if (transition_data["status"] == "pending" or transition_data["status"] == "rejected") and char_data["images"][transition_data["from_image"]]["status"] == "approved" and char_data["images"][transition_data["to_image"]]["status"] == "approved":
                    
                    output_path = f'{(character_staging_loc / transition_key).__str__()}.mp4'
                    transition_data["output_path"] = output_path

                    job_id = create_transition_video_job(
                        server_name, 
                        char_key,
                        char_data["images"][transition_data["from_image"]],
                        char_data["images"][transition_data["to_image"]],
                        transition_data
                    )
                    state["jobs"][job_id] = {
                        "type": "transition",
                        "character": char_key,
                        "image_id": "",
                        "transition_id": transition_key,
                        "status": "in_progress",
                        "output_path": output_path
                    }
                    transition_data["status"] = "processing"
                    transition_data["prompt_id"] = job_id
                    log_event("Transition Job created, updating state...")
                    # event_queue.put({
                    #     "type": "NEW_TRANSITION_JOB", 
                    #     "payload": {
                    #         "character": char_key,
                    #         "transition_key": transition_key
                    #         }
                    #     })
                    return state
                    # return f"Transition video job for {char_key} {transition_key}"
    
    
    #else if, if final video is pending, create a final video job condtion if all the transition videos for a character are approved, then create a final video job
    if state["characters"]:
        for char_key, char_data in state["characters"].items():
            character_staging_loc = staging_location / char_key
            character_staging_loc.mkdir(parents=True, exist_ok=True)
            final_video = char_data["final_video"]
            if final_video and (final_video["status"] == "pending" or final_video["status"] == "rejected") and all(transition_data["status"] == "approved" for transition_data in char_data["transitions"].values()):
                output_path = f'{(character_staging_loc / char_key).__str__()}.mp4'
                final_video["output_path"] = output_path
                job_id = create_final_video_job(server_name, char_key, char_data["transitions"])
                state["jobs"][job_id] = {
                    "type": "final_video",
                    "character": char_key,
                    "image_id": "",
                    "transition_id": "",
                    "status": "in_progress",
                    "output_path": output_path
                }
                final_video["status"] = "processing"
                final_video["prompt_id"] = job_id
                log_event("Final video Job created, updating state...")
                # event_queue.put({
                #     "type": "NEW_FINAL_VIDEO_JOB", 
                #     "payload": {
                #         "character": char_key
                #         }
                #     })
                return state
                # return f"Final video job for {char_key}"
    #else return None this will wait for next input
    # return "Image job for char1 img1"
    return state

def initiate_graph() :

    builder = StateGraph(RootState)

    builder.add_node("update_state_node", update_state)  # Placeholder for the actual function
    builder.add_node("persist_state_node", persist_state)  # Placeholder for the actual function
    builder.add_node("persist_state_node_2", persist_state)  # Placeholder for the actual function
    builder.add_node("create_next_job_node", create_next_job)  # Placeholder for the actual function

    builder.add_edge(START, "update_state_node")
    builder.add_edge("update_state_node", "persist_state_node")
    builder.add_edge("persist_state_node", "create_next_job_node")
    builder.add_edge("create_next_job_node", "persist_state_node_2")
    builder.add_edge("persist_state_node_2", END)

    return builder.compile()
