from typing import TypedDict, Optional, Dict, Literal

class ImageState(TypedDict):
    index: int
    expression_prompt: str
    expression: str
    pose_prompt: str
    pose: str
    from_time: float
    to_time: float
    status: Literal["pending", "processing", "approved", "rejected"] 
    prompt_id: Optional[str]
    output_path: Optional[str]

class TransitionState(TypedDict):
    from_image: str
    to_image: str
    status: Literal["pending", "processing", "approved", "rejected"]
    prompt_id: Optional[str]
    output_path: Optional[str]

class FinalVideoState(TypedDict):
    status: Literal["pending", "processing", "approved", "rejected"]
    prompt_id: Optional[str]
    output_path: Optional[str]

class CharacterState(TypedDict):
    outfit: str
    posture: Literal["standing", "sitting"]
    images: Dict[str, ImageState]
    transitions: Dict[str, TransitionState]
    final_video: FinalVideoState

class JobState(TypedDict):
    type: Literal["image", "transition", "final_video"]
    character: Literal["Aditya", "Ananya", "Arjun", "Naina", "Tara"]
    image_id: str
    transition_id: str
    status: Literal["in_progress", "completed", "failed", "sent_for_approval"]

class Event(TypedDict):
    type: str
    payload: dict

class RootState(TypedDict):
    id: str
    characters: Dict[Literal["Aditya", "Ananya", "Arjun", "Naina", "Tara"], CharacterState]
    jobs: Dict[str, JobState]   # key = prompt_id
    event: Optional[Event]