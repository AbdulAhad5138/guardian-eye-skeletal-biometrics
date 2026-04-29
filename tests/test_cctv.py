import requests
import os
import json

def test_real_cctv_clip():
    """
    Utility to test the security logic against a real CCTV video file.
    """
    print("\n--- 📹 CCTV Video Verification Test ---")
    
    # 1. Ask for inputs (or hardcode for quick test)
    video_path = input("[+] Enter the path to your video file (e.g. data/my_cctv.mp4): ")
    cred_id = input("[+] Enter the Credential ID to link this to (e.g. USER_01): ")
    
    if not os.path.exists(video_path):
        print(f"[!] Error: File '{video_path}' not found.")
        return

    # 2. Trigger the API
    api_url = "http://localhost:8000/api/access_event"
    payload = {
        "timestamp": 123456789.0,
        "credential_id": cred_id,
        "door_id": "TEST_GATE",
        "test_video_override": video_path
    }
    
    print(f"[*] Sending '{video_path}' to AI Engine for processing...")
    
    try:
        response = requests.post(api_url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("\n--- 🎯 AI ANALYSIS RESULT ---")
            print(f"Final Flag:  {result.get('flag')}")
            print(f"Confidence:  {round(result.get('confidence', 0) * 100, 1)}%")
            print(f"Reason:      {result.get('reason')}")
            print("\nExtracted Body Metrics:")
            print(json.dumps(result.get('metrics'), indent=4))
            print("\n[OK] Refresh your Streamlit Dashboard to see the full event log.")
        else:
            print(f"[!] API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[!] Connection Error: {e}. Make sure the API backend is running.")

if __name__ == "__main__":
    test_real_cctv_clip()
