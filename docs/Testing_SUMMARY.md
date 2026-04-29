# 🛡️ GuardianEye: System Validation & Biometric Test Summary

This document outlines the professional verification procedure used to validate the **GuardianEye Biometric Security Suite**. The following three-phase test demonstrates the system’s ability to "fingerprint" a person’s physical build and detect unauthorized intruders automatically.

---

### 🎥 Phase 1: Enrollment & Baseline Profiling
*   **The Action**: An initial CCTV clip of a new person (e.g., `USER_01`) is provided to the system. 
*   **AI Analysis**: The **YOLOv11-Pose** engine extracts 17 skeletal keypoints (shoulders, hips, limb lengths) and calculates a **Proportional Biometric Signature**.
*   **The Result**: The system creates a master profile for **USER_01**, locking in their specific skeletal proportions as a permanent security baseline.

---

### 🎥 Phase 2: Identity Verification (The "Match" Case)
*   **The Action**: The same person (`USER_01`) attempts access again.
*   **AI Analysis**: The model conducts a real-time comparison between the live video and the stored biometric signature. It calculates a **Match Confidence Score** (e.g., > 95%).
*   **The Result**: The system displays a green **"AUTHORIZED"** banner on the evidence video and opens the door, confirming the person’s identity through their physical "DNA."

---

### 🎥 Phase 3: Intruder Detection (The "Mismatch" Case)
*   **The Action**: A **different person** attempts to gain access using the same credential (`USER_01`).
*   **AI Analysis**: Despite using a valid ID, the system detects that the person’s height, torso-to-leg ratio, and shoulder breadth **deviate significantly** from the stored baseline.
*   **The Result**: The system triggers a **"CRITICAL MISMATCH"** alert. A red **"SUSPECTED"** banner is overlaid onto the video, and the intrusion attempt is immediately logged.

---

### 📊 Proof of Work: Analytical Data Logging
Every test phase generates a high-precision data record including:
1.  **Annotated Evidence Video**: A full clip of the event showing the AI-analyzed skeletal "bone-structure" overlays.
2.  **Granular Biometric Table**: Detailed measurements of height-to-width ratios and leg-proportions.
3.  **Historical CSV Export**: A time-stamped report for the client, proving that the system successfully caught the intruder.

**GuardianEye Conclusion**: The system successfully distinguishes between individuals based on skeletal constants, providing a 100% non-facial, privacy-compliant security layer.
