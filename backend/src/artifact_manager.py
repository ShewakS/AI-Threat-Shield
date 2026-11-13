import os
import joblib

class ArtifactManager:
    def __init__(self, artifact_dir='artifacts'):
        self.artifact_dir = artifact_dir
        os.makedirs(self.artifact_dir, exist_ok=True)

    def save_artifacts(self, model, feature_engineer, feature_selector, model_name="Best Model"):
        print(f"\nSaving trained artifacts to '{self.artifact_dir}'...")
        
        artifacts = {
            'best_model.pkl': model,
            'feature_engineer.pkl': feature_engineer,
            'feature_selector.pkl': feature_selector,
            'metadata.pkl': {'model_name': model_name}
        }
        
        for filename, obj in artifacts.items():
            filepath = os.path.join(self.artifact_dir, filename)
            joblib.dump(obj, filepath)
            print(f"Saved {filename} -> {filepath}")

    def load_artifacts(self):
        print(f"Loading artifacts from '{self.artifact_dir}'...")
        
        artifacts = {}
        for filename in ['best_model.pkl', 'feature_engineer.pkl', 'feature_selector.pkl', 'metadata.pkl']:
            filepath = os.path.join(self.artifact_dir, filename)
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"Artifact missing: {filepath}. Please run train.py first.")
            artifacts[filename.replace('.pkl', '')] = joblib.load(filepath)
            
        return artifacts
