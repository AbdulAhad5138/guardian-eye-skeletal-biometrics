import json
import os
from typing import Dict, Any

class ProfileDatabase:
    """
    Manages non-facial biometric profiles linked to specific Credential IDs.
    Calculates a "Rolling Mean" of features to account for natural variation (clothing, walking style).
    """

    def __init__(self, db_path="data/profiles/profiles.json"):
        self.db_path = db_path
        self.ensure_db()
        self.profiles = self.load_db()

    def ensure_db(self):
        if not os.path.exists(os.path.dirname(self.db_path)):
            os.makedirs(os.path.dirname(self.db_path))
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({}, f)

    def load_db(self) -> Dict:
        try:
            if not os.path.exists(self.db_path): 
                with open(self.db_path, "w") as f: json.dump({}, f)
            with open(self.db_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def reload(self):
        """Forces the database to re-read from disk (useful for UI resets)."""
        self.profiles = self.load_db()

    def save_db(self):
        with open(self.db_path, "w") as f:
            json.dump(self.profiles, f, indent=4)

    def update_profile(self, cred_id: str, new_metrics: Dict):
        """
        Calculates a new arithmetic mean for the user profile using the incremental average formula.
        :param cred_id: Unique identifier for the user's credential.
        :param new_metrics: New physical data extracted from the current detection.
        """
        if cred_id not in self.profiles:
            # Registration phase: Create initial profile
            self.profiles[cred_id] = {
                "entry_count": 1,
                "metrics": new_metrics
            }
        else:
            profile = self.profiles[cred_id]
            count = profile["entry_count"]
            current_metrics = profile["metrics"]
            
            # Recalculate average: (Old Mean * count + New Val) / (count + 1)
            updated_metrics = {}
            for key, val in new_metrics.items():
                if key in current_metrics:
                    updated_metrics[key] = (current_metrics[key] * count + val) / (count + 1)
                else:
                    updated_metrics[key] = val
            
            self.profiles[cred_id] = {
                "entry_count": count + 1,
                "metrics": updated_metrics
            }
        self.save_db()

    def get_profile(self, cred_id: str) -> Dict:
        return self.profiles.get(cred_id, {}).get("metrics", None)

    def get_all_profiles(self) -> Dict:
        return self.profiles
