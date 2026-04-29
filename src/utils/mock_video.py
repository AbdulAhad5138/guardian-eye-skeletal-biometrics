import cv2
import numpy as np
import os

def create_synthetic_test_video(output_path, person_type="A"):
    """
    Creates a simulated video clip of a person (represented as a rectangle)
    moving across the camera view.
    Person A: Tall and thin (180cm, 50kg profile)
    Person B: Shorter and wider (160cm, 90kg profile)
    """
    width, height = 640, 480
    fps = 30
    duration_sec = 3
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Person dimensions (simulated)
    if person_type == "A":
        p_w, p_h = 40, 180  # Tall/Thin
    else:
        p_w, p_h = 100, 110  # Short/Stout (Very different from A)
    
    for i in range(fps * duration_sec):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        # Background: Gray
        frame[:] = (50, 50, 50)
        
        # Horizontal movement: Walk from left to right center
        x_pos = 100 + (i * 2) 
        y_pos = height - p_h - 10 # Stay on "ground"
        
        # Draw "Person" (Stick Figure)
        color = (255, 255, 255)
        # Head
        cv2.circle(frame, (x_pos + p_w//2, y_pos + p_h//5), p_w//2, color, -1)
        # Body
        cv2.line(frame, (x_pos + p_w//2, y_pos + p_h//5), (x_pos + p_w//2, y_pos + 3*p_h//4), color, 2)
        # Arms
        cv2.line(frame, (x_pos + p_w//2, y_pos + p_h//3), (x_pos, y_pos + p_h//2), color, 2)
        cv2.line(frame, (x_pos + p_w//2, y_pos + p_h//3), (x_pos + p_w, y_pos + p_h//2), color, 2)
        # Legs
        cv2.line(frame, (x_pos + p_w//2, y_pos + 3*p_h//4), (x_pos, y_pos + p_h), color, 2)
        cv2.line(frame, (x_pos + p_w//2, y_pos + 3*p_h//4), (x_pos + p_w, y_pos + p_h), color, 2)
        
        # Draw "Entry Line" (Red)
        cv2.line(frame, (0, height//2), (width, height//2), (0, 0, 255), 2)
        
        out.write(frame)
        
    out.release()
    print(f"[+] Synthetic video '{output_path}' generated for Person Type {person_type}")

if __name__ == "__main__":
    if not os.path.exists("data/test_clips"):
        os.makedirs("data/test_clips")
    create_synthetic_test_video("data/test_clips/person_a.mp4", "A")
    create_synthetic_test_video("data/test_clips/person_b.mp4", "B")
