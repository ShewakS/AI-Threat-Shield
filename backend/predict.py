import argparse
import os
import sys
import numpy as np
import pandas as pd

from src.artifact_manager import ArtifactManager

THREAT_LEVELS = {
    'Ham': ('LOW', 'Minimal security risk detected. Message/URL appears legitimate.'),
    'Spam': ('MEDIUM', 'Unsolicited promotional/commercial content detected. Caution advised.'),
    'Phishing': ('CRITICAL', 'Severe security threat! High probability of credential theft or malware delivery.')
}

CLASS_NAMES = {0: 'Ham', 1: 'Spam', 2: 'Phishing'}

def main():
    parser = argparse.ArgumentParser(description="Predict Spam & Phishing threat level for a new SMS, email, or URL sample")
    parser.add_argument("--text", type=str, required=True, help="SMS message, email text, or URL string to classify")
    args = parser.parse_args()

    # Load saved pipeline artifacts
    try:
        artifact_mgr = ArtifactManager(artifact_dir='artifacts')
        artifacts = artifact_mgr.load_artifacts()
    except Exception as e:
        print(f"[Error] Failed to load trained model artifacts: {e}")
        print("Please run `python train.py` first to train the model and save artifacts.")
        sys.exit(1)

    best_model = artifacts['best_model']
    feature_engineer = artifacts['feature_engineer']
    feature_selector = artifacts['feature_selector']
    metadata = artifacts['metadata']

    input_text = args.text.strip()
    df_sample = pd.DataFrame([{'text': input_text}])

    # Transform features
    feats = feature_engineer.transform(df_sample)
    feats_sel = feature_selector.transform(feats)

    # Predict class
    pred_idx = best_model.predict(feats_sel)[0]
    pred_class = CLASS_NAMES.get(pred_idx, 'Unknown')

    # Confidence score & Probabilities
    confidence = 0.0
    probs = {}
    if hasattr(best_model, 'predict_proba'):
        try:
            proba_arr = best_model.predict_proba(feats_sel)[0]
            confidence = float(np.max(proba_arr)) * 100.0
            for idx, prob in enumerate(proba_arr):
                c_name = CLASS_NAMES.get(idx, f"Class_{idx}")
                probs[c_name] = f"{prob*100.0:.2f}%"
        except Exception:
            confidence = 100.0
    else:
        confidence = 100.0

    threat_level, threat_desc = THREAT_LEVELS.get(pred_class, ('UNKNOWN', 'Unable to assess threat level.'))

    # Feature Explanation
    top_explanations = []
    try:
        if hasattr(best_model, 'coef_'):
            coefs = best_model.coef_[pred_idx] if best_model.coef_.ndim > 1 else best_model.coef_[0]
            if scipy.sparse.issparse(feats_sel):
                dens = feats_sel.toarray()[0]
            else:
                dens = feats_sel[0]
            contribs = coefs * dens
            top_idx = np.argsort(np.abs(contribs))[::-1][:3]
            selected_names = [feature_engineer.feature_names[i] for i in feature_selector.selected_indices]
            for ti in top_idx:
                if contribs[ti] != 0:
                    top_explanations.append(f"{selected_names[ti]} (impact: {contribs[ti]:+.4f})")
    except Exception:
        pass

    print("\n" + "="*60)
    print(" AUTOMATED SPAM & PHISHING DETECTION REPORT ")
    print("="*60)
    print(f" Input Content:      \"{input_text[:100]}{'...' if len(input_text) > 100 else ''}\"")
    print(f" Model Engine:       {metadata.get('model_name', 'Trained Model')}")
    print(f" Predicted Category: {pred_class.upper()}")
    print(f" Confidence Score:   {confidence:.2f}%")
    print(f" Threat Level:       {threat_level}")
    print(f" Assessment Note:    {threat_desc}")
    if probs:
        print(f" Class Breakdown:    {probs}")
    if top_explanations:
        print(f" Top Indicators:     {', '.join(top_explanations)}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
