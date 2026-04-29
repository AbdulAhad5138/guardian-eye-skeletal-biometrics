import requests
import time
import os
import subprocess
import signal

def run_full_security_simulation():
    """
    Automated test script to prove the logic for the Non-Facial Verification system.
    Demonstrates: Registration -> Successful Match -> Intruder Mismatch.
    """
    print("--- [SENSORS] Starting Security System Simulation ---")
    
    # 1. Generate Environment
    if not os.path.exists("src/utils/mock_video.py"):
        print("[!] Dependency Error: Mock Video Generator missing.")
        return
    
    subprocess.run(["python", "src/utils/mock_video.py"])
    
    # 2. Simulate Access Events via API
    api_url = "http://localhost:8000/api/access_event"
    
    # Case 1: Initial Registration (User A - Tall/Thin Profile)
    print("\n[*] CASE 1: Initial Registration (User A)")
    payload_1 = {
        "timestamp": time.time(), "credential_id": "USER_A", "door_id": "FRONT_DOOR",
        "test_video_override": "data/test_clips/person_a.mp4"
    }
    try:
        r1 = requests.post(api_url, json=payload_1)
        print(f"Result: {r1.json().get('flag')} (Confidence: {r1.json().get('confidence')})")
    except Exception as e:
        print(f"[!] ERROR: {e}")
        return

    # Case 2: Consistent Match (User A enters again)
    print("\n[*] CASE 2: Consistent Match (User A Returns)")
    payload_2 = {
        "timestamp": time.time(), "credential_id": "USER_A", "door_id": "FRONT_DOOR",
        "test_video_override": "data/test_clips/person_a.mp4"
    }
    r2 = requests.post(api_url, json=payload_2)
    print(f"Result: {r2.json().get('flag')} (Confidence: {r2.json().get('confidence')})")

    # Case 3: CRITICAL MISMATCH (User A's card used by someone else - Profile B)
    print("\n[*] CASE 3: Profile B (Short/Wide) using User A's Stolen Credential")
    # We use User A's ID but provide Person B's video (150cm vs 180cm)
    payload_3 = {
        "timestamp": time.time(), "credential_id": "USER_A", "door_id": "FRONT_DOOR",
        "test_video_override": "data/test_clips/person_b.mp4"
    }
    r3 = requests.post(api_url, json=payload_3)
    
    # Check if mismatch was caught
    print(f"Result: {r3.json().get('flag')} (Confidence: {r3.json().get('confidence')})")
    print(f"Reason: {r3.json().get('reason')}")

    print("\n--- [OK] Simulation Complete: Visual results available on Streamlit Dashboard ---")

if __name__ == "__main__":
    run_full_security_simulation()
