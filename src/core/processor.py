import cv2
import time
import numpy as np
import pandas as pd
from ultralytics import YOLO
from src.core.metrics import BodyMetricsEngine
from src.database.storage import ProfileDatabase

class SecurityVisionController:
    """
    Main controller for video-based security verification.
    Syncs with Access Control Events and runs AI inference.
    """
    
    def __init__(self, model_path="yolo11n-pose.pt", db_path="data/profiles/profiles.json"):
        # Initialize YOLOv11-Pose (Ultra-Fast for Real-Time)
        self.model = YOLO(model_path)
        self.engine = BodyMetricsEngine()
        self.db = ProfileDatabase(db_path)
        
        # Configuration for "Line Crossing" (Y-coordinate as percentage of frame)
        self.entry_line_y = 0.5 
        
    def process_video_window(self, video_source, cred_id, door_id, is_registration=False):
        """
        Processes a short clip to identify the entrant and compute similarity scores.
        :param is_registration: If True, only store the baseline without comparison.
        """
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            return {"error": "Video feed unavailable", "status": "failed"}

        # --- NEW: Evidence Video Setup (Using ImageIO for reliable H264) ---
        import os
        import imageio
        evid_dir = "data/evidence"
        if not os.path.exists(evid_dir): os.makedirs(evid_dir)
        evid_path = os.path.join(evid_dir, f"evidence_{int(time.time())}.mp4")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0: fps = 24.0 # Fallback
        
        # High-Quality H264 Writer (macro_block_size=None for non-16x resolutions)
        writer = imageio.get_writer(evid_path, fps=fps, codec='libx264', quality=8, macro_block_size=None)
        # ------------------------------------------------------------------

        results_list = []
        person_track_id = None
        
        # Frame Analysis Phase
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # YOLO Pose Inference
            results = self.model.track(frame, persist=True, verbose=False)[0]
            
            # --- NEW: Draw Annotations for evidence video ---
            annotated_frame = results.plot() # Built-in YOLO method for keypoints/skeletons
            # Convert BGR to RGB for ImageIO
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            writer.append_data(rgb_frame)
            # ----------------------------------------------

            if results.boxes is None or len(results.boxes) == 0:
                continue

            # Find the largest/closest person (highest area)
            boxes = results.boxes.xywh.cpu().numpy()
            areas = boxes[:, 2] * boxes[:, 3]
            best_idx = np.argmax(areas)
            
            # Extract keypoints and box info
            keypoints = results.keypoints.xy[best_idx].cpu().numpy()
            box = boxes[best_idx]
            
            # 1. Feature Extraction
            current_metrics = self.engine.extract_from_keypoints(keypoints, box[2], box[3])
            
            # 2. Check Historical Profile
            historical_profile = self.db.get_profile(cred_id)
            
            if historical_profile and not is_registration:
                # Comparison Phase
                confidence = self.engine.calculate_similarity_score(current_metrics, historical_profile)
                is_match = (confidence > 0.75) # threshold
            else:
                # New Registration or First Entry: Initial Confidence is 100%
                confidence = 1.0
                is_match = True
            
            # Append findings to results list
            results_list.append({
                "cred_id": cred_id,
                "confidence": confidence,
                "metrics": current_metrics,
                "is_match": is_match,
                "frame": frame.copy()
            })

        cap.release()
        writer.close() # Close evidence video writer
        
        if not results_list:
            return {"error": "No person detected in window", "status": "incomplete"}

        # --- NEW: STABLE SIGNATURE SELECTION (Zero-Error Logic) ---
        # Instead of taking the 'best' frame (which might be a spike), we take 
        # the MEDIAN biometric signature across the entire window.
        all_metrics_df = pd.DataFrame([r["metrics"] for r in results_list])
        stable_metrics = all_metrics_df.median().to_dict()
        
        # Calculate Final Confidence based on the Stable Signature
        historical_profile = self.db.get_profile(cred_id)
        if historical_profile and not is_registration:
            confidence = self.engine.calculate_similarity_score(stable_metrics, historical_profile)
            is_match = (confidence >= 0.85) # High-Security Threshold
        else:
            confidence = 1.0
            is_match = True
            
        best_event = {
            "cred_id": cred_id,
            "metrics": stable_metrics,
            "confidence": confidence,
            "is_match": is_match
        }
        
        # --- NEW: Automated Alerting & Logic Determination ---
        if is_registration:
            best_event["flag"] = "ENROLLED"
            best_event["reason"] = "Initial biometric baseline established."
            self.db.update_profile(cred_id, best_event["metrics"])
            overlay_text = f"ENROLLING: {cred_id}"
            overlay_color = (255, 255, 0) # Cyan/Yellow
        elif not best_event["is_match"]:
            best_event["flag"] = "CRITICAL_MISMATCH"
            best_event["reason"] = f"Detected physical build deviates by {round((1-best_event['confidence'])*100, 1)}% from history."
            overlay_text = "SUSPECTED: IDENTITY MISMATCH"
            overlay_color = (0, 0, 255) # Red
        else:
            best_event["flag"] = "VERIFIED"
            best_event["reason"] = "Stable body metrics match historical profile."
            # Only update profile baseline if the match is extremely reliable (>92%)
            if confidence > 0.92:
                self.db.update_profile(cred_id, best_event["metrics"])
            
            overlay_text = f"AUTHORIZED: {cred_id}"
            overlay_color = (0, 150, 0) # Green

        # --- RE-GENERATE VIDEO WITH OVERLAYS (Professional touch) ---
        # We RE-OPEN the writer to add the final text overlays to every frame
        writer.close() # Close first pass
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        final_writer = imageio.get_writer(evid_path, fps=fps, codec='libx264', quality=8)
        
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame_idx > 120: break # Process max 5 seconds for evidence
            
            # Use YOLO to get the skeleton for this frame again
            results = self.model.track(frame, persist=True, verbose=False, show=False)[0]
            annotated_frame = results.plot()
            
            # --- ADD STATUS OVERLAY ---
            # Semi-transparent background for text
            cv2.rectangle(annotated_frame, (10, 10), (450, 60), (0,0,0), -1)
            cv2.putText(annotated_frame, overlay_text, (20, 45), 
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, overlay_color, 2)
            
            rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            final_writer.append_data(rgb_frame)
            frame_idx += 1
            
        cap.release()
        final_writer.close()
        
        best_event["evidence_video"] = evid_path
        return best_event

    def simulate_access_event(self, event_data: dict, video_clip: str):
        """
        High-level trigger for backend integration.
        :param event_data: {cred_id, timestamp, door_id}
        """
        print(f"[*] Access Event System Triggered: Credential {event_data['cred_id']} at {event_data['door_id']}")
        analysis = self.process_video_window(video_clip, event_data['cred_id'], event_data['door_id'])
        
        # Save analysis log
        with open(f"data/events/event_{int(time.time())}.json", "w") as f:
            log_data = analysis.copy()
            if "frame" in log_data: del log_data["frame"] # Don't save binary frame to JSON
            json.dump(log_data, f, indent=4)
            
        print(f"[!] Analysis Complete: Result -> {analysis.get('flag')} (Confidence: {analysis.get('confidence', 0)})")
        return analysis
