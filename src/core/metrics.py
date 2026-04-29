import numpy as np

class BodyMetricsEngine:
    """
    Extracted non-facial physical features for a specific person in a frame.
    Calculates normalized biometric signature that is camera-angle resistant.
    """
    
    def __init__(self, reference_height_px=None, door_height_cm=203):
        """
        :param reference_height_px: Number of pixels for a known object (like doorway)
        :param door_height_cm: Actual height of referene object in cm (Standard door is 203cm/80in)
        """
        self.door_height_cm = door_height_cm
        self.pixels_per_cm = None 
        if reference_height_px:
            self.pixels_per_cm = reference_height_px / door_height_cm

    def extract_from_keypoints(self, keypoints, box_width, box_height):
        """
        Extract metrics from keypoints using PROPORTIONAL ANCHORING.
        Instead of using raw pixels, we use ratios against the torso-width 
        to ensure the signature is the same whether far or near.
        """
        # Shoulder Width is our most stable reference anchor for scaling
        shoulder_width = abs(keypoints[5][0] - keypoints[6][0])
        if shoulder_width < 10: shoulder_width = box_width * 0.4 # Fallback to box-width ratio

        # 1. Height Anchor (Total Height / Shoulder Width)
        feet_y = (keypoints[15][1] + keypoints[16][1]) / 2
        head_y = keypoints[0][1]
        pixel_height = feet_y - head_y
        if pixel_height < 10: pixel_height = box_height
        
        height_anchor = pixel_height / shoulder_width

        # 2. Torso-to-Leg Ratio (Anatomical Constant)
        shoulder_y = (keypoints[5][1] + keypoints[6][1]) / 2
        hip_y = (keypoints[11][1] + keypoints[12][1]) / 2
        torso_len = hip_y - shoulder_y
        leg_len = feet_y - hip_y
        torso_leg_ratio = torso_len / max(leg_len, 0.1)

        # 3. Shoulder-to-Hip Breadth Ratio
        hip_width = abs(keypoints[11][0] - keypoints[12][0])
        if hip_width < 1: hip_width = shoulder_width * 0.8
        shoulder_hip_ratio = shoulder_width / hip_width

        # 4. Frame Box Ratio
        frame_index = box_width / max(pixel_height, 0.1)

        return {
            "estimated_height": float(pixel_height), # For reference log
            "biometric_signature": float(height_anchor), # Core stable biometric
            "torso_leg_ratio": float(torso_leg_ratio),
            "shoulder_hip_ratio": float(shoulder_hip_ratio),
            "frame_index": float(frame_index)
        }

    @staticmethod
    def calculate_similarity_score(current_metrics, historical_profile):
        """
        Strict Biometric Comparison using Weighted Deviation.
        """
        # High confidence requires stability in the skeletal constants
        weights = {
            "biometric_signature": 0.5, # Height/Width Anchor
            "torso_leg_ratio": 0.3,     # Leg/Torso symmetry
            "shoulder_hip_ratio": 0.1,  # Frame breadth
            "frame_index": 0.1          # Bounding Box profile
        }
        
        total_dist = 0
        comparisons = 0
        
        for key, weight in weights.items():
            curr = current_metrics.get(key, 0)
            target = historical_profile.get(key, 0)
            
            if target > 0 and curr > 0:
                # Percentage Deviation
                deviation = abs(curr - target) / target
                # We use an exponential penalty: small diffs pass, big ones fail fast.
                penalty = min(deviation * 2, 1.0) # Multiply by 2 makes 25% diff a 50% penalty
                total_dist += weight * penalty
                comparisons += 1
            else:
                # Missing comparison: Significant penalty for unreliable scan
                total_dist += weight * 0.5 

        # We normalize the result
        confidence = 1.0 - total_dist
        return round(max(confidence, 0.0), 3)
