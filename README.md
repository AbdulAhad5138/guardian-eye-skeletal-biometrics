# 🛡️ GuardianEye: Professional Biometric Access Suite

GuardianEye is a high-precision, non-facial biometric verification system. It uses **YOLOv11-Pose** to analyze skeletal proportions and verify if the person using a credential matches the historical physical profile.

## 🚀 One-Step Launch
You no longer need to run multiple terminals. Everything is now unified in a single Professional UI.
```bash
streamlit run app.py
```

## 🧠 Key Logic: "The Skeletal Signature"
Unlike standard security systems that can be fooled by clothing or masks, GuardianEye analyzes the **Bone-Structure Proportions**:
- **Normalized Height Index**: Calculates real height regardless of camera distance.
- **Torso-to-Leg Ratio**: A unique physical constant for every individual.
- **Shoulder-to-Hip Breadth**: Analyzes the "Frame" or "Build" of the person.
- **Weighted Match Scoring**: Uses a 75% similarity threshold to trigger alarms.

## 📁 Storage & Logs
- **Profiles**: Stored in `data/profiles/` (The "Memory" of authorized people).
- **Events**: Stored in `data/events/` (The log of every access attempt).
- **Evidence**: Stored in `data/evidence/` (The annotated videos showing joints/bones).

### 2. Normalized Biometric Signature
To solve the "Perspective Problem" (people looking smaller further away), I implemented a **Proportional Profile**. 
- Instead of measuring "height in pixels," we measure the **Ratio** of body parts to each other. 
- A person's Torso-to-Leg ratio remains constant regardless of distance from the camera.

### 3. Stability via Incremental Average
A person might be carrying a bag one day or slouching the next. 
**The Logic:** Each "Match" updates the historical profile using an **Incremental Mean Formula**. This allows the system to "learn" the natural variance of the user's gait and build over time, reducing false positives.

### 4. Weighted Similarity Scoring
We use a **Weighted Euclidean Distance** algorithm. 
- **Height Index (50% Weight)**: The most stable feature.
- **Limb Ratios (20% Weight)**: Stable but affected by walking speed.
- **Frame Index (15% Weight)**: Width/Volumetric data.
If the final confidence falls below **75%**, a `CRITICAL_MISMATCH` flag is raised.

---

## 🚀 How to Run (Testing Phase)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Backend (Logic & Database)
```bash
python src/api/main_api.py
```

### 3. Start the UI Dashboard
```bash
streamlit run app.py
```

### 4. Run the Full Simulation (Automatic Test)
```bash
python tests/run_simulation.py
```
This script will generate synthetic videos of different people and trigger the API to prove the Mismatch logic works.
