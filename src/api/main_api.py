import os
import time
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from src.core.processor import SecurityVisionController

app = FastAPI(title="Security Verifier API")
controller = SecurityVisionController()

class AccessEvent(BaseModel):
    timestamp: float
    credential_id: str
    door_id: str
    test_video_override: str = None # For simulation only

@app.post("/api/access_event")
async def handle_access_event(event: AccessEvent):
    """
    Endpoint for external door controller to trigger verification.
    """
    # Logic: Fetch corresponding video from buffer or RTSP stream
    # For prototype simulation:
    if event.test_video_override:
        video_path = event.test_video_override
    else:
        # Default behavior: guess based on ID
        video_path = f"data/test_clips/person_{event.credential_id[-1].lower()}.mp4"
    if not os.path.exists(video_path):
        video_path = "data/test_clips/person_a.mp4" # Default fallback
    
    try:
        analysis = controller.process_video_window(video_path, event.credential_id, event.door_id)
        
        # --- NEW: Save event log for Dashboard ---
        log_dir = "data/events"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_filename = f"event_{int(time.time())}_{event.credential_id}.json"
        with open(os.path.join(log_dir, log_filename), "w") as f_log:
            log_data = analysis.copy()
            if "frame" in log_data: del log_data["frame"] # Avoid saving binary image to JSON
            json.dump(log_data, f_log, indent=4)
        # -----------------------------------------

        return {
            "status": "processed",
            "flag": analysis.get("flag"),
            "confidence": analysis.get("confidence"),
            "reason": analysis.get("reason"),
            "metrics": analysis.get("metrics"),
            "evidence_video": analysis.get("evidence_video")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/history")
async def get_event_history():
    """
    Quick dashboard JSON feed for logs.
    """
    history = []
    log_dir = "data/events"
    if os.path.exists(log_dir):
        for f in os.listdir(log_dir):
            if f.endswith(".json"):
                with open(os.path.join(log_dir, f), "r") as f_in:
                    history.append(json.load(f_in))
    return history[::-1] # Reverse cron

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
