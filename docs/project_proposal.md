# Project Proposal: Non-Facial Video Verification System

## 1. Simple Summary (For You)
The client wants a "Body-Based Security Guard" that works behind the scenes. 
When someone scans their card at a door, the system looks at the camera, measures the person's physical build (height, shoulder width, body shape), and checks if that build matches the "normal" person who uses that card.

**Goal:** Catch someone if they steal a card or if two people enter on one scan, but *without* using facial recognition (which is better for privacy and legal reasons).

---

## 2. Deep Technical Analysis
The system is an **Event-Driven Video Analytic Pipeline**. It bridges the gap between hardware access control (the card reader) and software video analysis (YOLO/OpenCV).

### A. The Core Logic Workflow
1.  **Event Integration**: An API endpoint receives a JSON payload (timestamp, credential_id, door_id) from the door controller.
2.  **Time-Synchronized Buffer**: The system requests a segment of video (e.g., 10 seconds) from the NVR/Camera stream based on the event timestamp.
3.  **Entry Validation (Line Crossing)**: We use computer vision to ensure the person actually crossed the door line within 1-2 seconds of the scan.
4.  **Body-Metrics Extraction**:
    - **Height Estimation**: Uses camera geometry (vanishing points) or a known reference (the door frame). 
    - **Physical Signature**: A multi-dimensional vector representing shoulder-to-hip ratio, limb-to-torso ratio, and overall body "volume" (bounding box density).
5.  **Historical Profile Comparison**:
    - **Registration Phase**: The first several entries for a new ID build the baseline "Person Profile."
    - **Verification Phase**: Subsequent entries are compared against the average of this baseline.
6.  **Anomaly Detection**: If the "Similarity Score" drops below a specific threshold (e.g., 75%), an alert is generated.

### B. Technical Stack Recommendation
- **Detection Engine**: YOLOv8 or YOLOv11 (specifically the `pose` model to get skeletal landmarks for better height/proportion accuracy).
- **Video Handling**: Python with `OpenCV` (for RTSP stream processing) and `FFmpeg` for clip extraction.
- **Data Storage**: PostgreSQL (for logs) + NumPy/Protobuf (for efficient storage of body signatures).
- **Backend**: FastAPI (asynchronous to handle high-frequency door events).

---

## 3. Risks & Limitations
| Risk | Description | Mitigation |
| :--- | :--- | :--- |
| **Clothing Changes** | Heavy coats vs. t-shirts change body volume. | Use skeletal landmarks (joints/bones) which are less affected by clothing than simple bounding boxes. |
| **Camera Perspective** | High-angle cameras distort height. | Use homography-based calibration to calculate the "real-world" height. |
| **Multi-Person Entry** | Two people walking through together. | Implement "Re-ID" (Re-Identification) models to separate and track distinct body signatures. |
| **Lighting** | Grainy video at night affects precision. | Implement a confidence-score threshold; if the image is too dark, flag for manual review instead of failing automatically. |

---

## 4. Response for the Client
*You can copy and adapt this for your message back to them:*

### Similar Systems Experience
"I have experience building computer vision systems for object tracking and classification, including:
- A YOLOv11-based detection and classification pipeline for agricultural monitoring.
- High-precision biometric identification systems (Face/Body analysis).
- Real-time video stream processing using RTSP and OpenCV."

### Proposed Logic Structure
1. **Trigger Phase**: Webhook-based integration with the access control system.
2. **Video Retrieval**: Automated scraping of a 10s window around the timestamp from the RTSP stream.
3. **Analytics Phase**:
   - YOLO-based person detection + Pose Estimation.
   - Spatial calibration to calculate absolute height and limb proportions.
   - Filtering out background traffic via line-crossing logic.
4. **Scoring Phase**: Calculating the distance (Euclidean/Cosine) between the current entry and the historical "Credential Profile."
5. **UI Phase**: A FastAPI + Streamlit dashboard for review and flagging.

### Time & Cost Estimate
- **Phase 1: Proof of Concept (2-3 weeks)**: Build the basic YOLO detector + height extraction logic on static clips.
- **Phase 2: Full Logic & Integration (4-6 weeks)**: Integrate RTSP streams, historical scoring, and the alerting dashboard.
- **Total Development Estimate**: 8-9 weeks.
- **Cost**: $[Insert Your Rate here] (approx. $10,000 - $15,000 for a production-ready prototype).
