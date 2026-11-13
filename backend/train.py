import argparse
import sys
import os
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split

from src.data_loader import load_and_preprocess_dataset
from src.feature_engineering import FeatureEngineer
from src.feature_selector import FeatureSelector
from src.model_trainer import ModelTrainer
from src.evaluator import Evaluator
from src.artifact_manager import ArtifactManager

def main():
    parser = argparse.ArgumentParser(description="Spam and Phishing Detection Machine Learning Training Pipeline")
    parser.add_argument("--sample-size", type=int, default=30000, help="Number of records to sample for training (default: 30000, use 0 for all)")
    parser.add_argument("--max-features", type=int, default=5000, help="Maximum TF-IDF features (default: 5000)")
    parser.add_argument("--select-k", type=int, default=3000, help="Top K features to select (default: 3000)")
    parser.add_argument("--tune", action="store_true", help="Perform hyperparameter tuning on the best model")
    parser.add_argument("--pca", action="store_true", help="Apply PCA (TruncatedSVD) dimensionality reduction")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    args = parser.parse_args()

    sample_size = None if args.sample_size <= 0 else args.sample_size

    print("="*70)
    print(" SPAM & PHISHING DETECTION MACHINE LEARNING PIPELINE ")
    print("="*70)
    print(f"Sample Size:   {sample_size if sample_size else 'All'}")
    print(f"TF-IDF Max:    {args.max_features}")
    print(f"Select K:      {args.select_k}")
    print(f"PCA Reduction: {args.pca}")
    print(f"Tuning Enabled:{args.tune}")
    print(f"Random State:  {args.seed}")
    print("="*70)

    # 1. Load and merge datasets
    df = load_and_preprocess_dataset(sample_size=sample_size, random_state=args.seed)

    # 2. Stratified Train-Test Split (80:20)
    print("\nSplitting dataset into 80% Train and 20% Test subsets...")
    train_df, test_df, y_train, y_test = train_test_split(
        df, df['label'], test_size=0.20, stratify=df['label'], random_state=args.seed
    )
    print(f"Train samples: {len(train_df)} | Test samples: {len(test_df)}")

    # 3. Feature Engineering
    print("\nPerforming advanced feature engineering...")
    fe = FeatureEngineer(max_tfidf_features=args.max_features)
    X_train_feats = fe.fit_transform(train_df)
    X_test_feats = fe.transform(test_df)
    print(f"Extracted feature matrix shape: {X_train_feats.shape}")

    # 4. Feature Selection
    print("\nApplying feature selection...")
    selector = FeatureSelector(k=args.select_k, score_func='chi2', use_pca=args.pca, n_components=100)
    X_train_sel = selector.fit_transform(X_train_feats, y_train)
    X_test_sel = selector.transform(X_test_feats)
    print(f"Selected feature matrix shape: {X_train_sel.shape}")

    # 5. Train Supervised Models
    print("\nTraining supervised machine learning algorithms...")
    trainer = ModelTrainer(random_state=args.seed)
    trained_models = trainer.train_all(X_train_sel, y_train)

    # 6. Evaluate Models (Checking for Overfitting & Underfitting)
    evaluator = Evaluator(plot_dir='plots')
    results_df, model_preds, model_probs = evaluator.compare_models(trained_models, X_train_sel, y_train, X_test_sel, y_test)

    # Print comparative summary table
    print("\n" + "="*80)
    print(" FINAL COMPARATIVE PERFORMANCE SUMMARY & OVERFITTING DIAGNOSIS ")
    print("="*80)
    print(results_df.to_string(index=False))

    # 7. Select Best Model
    best_model_name = results_df.iloc[0]['Model']
    best_model = trained_models[best_model_name]
    print(f"\n>>> Best Performing Model Selected: '{best_model_name}' (F1-Score: {results_df.iloc[0]['F1-Score']:.4f})")

    # 8. Hyperparameter Optimization (Optional)
    if args.tune:
        best_model = trainer.tune_best_model(best_model_name, best_model, X_train_sel, y_train)
        # Re-evaluate tuned model
        m, y_pred, y_prob = evaluator.evaluate_model(best_model, X_train_sel, y_train, X_test_sel, y_test, model_name=f"{best_model_name} (Tuned)")
        print(f"\nTuned Model Performance:")
        print(f"Train Accuracy: {m['Train Accuracy']:.4f} | Test Accuracy: {m['Test Accuracy']:.4f} | Gap: {m['Accuracy Gap']:+.4f} [{m['Fit Status']}]")
        print(f"Precision: {m['Precision']:.4f} | Recall: {m['Recall']:.4f} | F1: {m['F1-Score']:.4f}")
        model_preds[best_model_name] = y_pred
        model_probs[best_model_name] = y_prob

    # 9. Plot Evaluation Charts
    print("\nGenerating graphical visualizations in 'plots/'...")
    evaluator.plot_confusion_matrix(y_test, model_preds[best_model_name], model_name=best_model_name)
    evaluator.plot_roc_curves(y_test, model_probs[best_model_name], model_name=best_model_name)
    evaluator.plot_precision_recall_curves(y_test, model_probs[best_model_name], model_name=best_model_name)
    evaluator.plot_model_comparison(results_df)

    # Feature Importance Plot
    if selector.selected_indices is not None and len(fe.feature_names) >= max(selector.selected_indices):
        selected_feature_names = [fe.feature_names[i] for i in selector.selected_indices]
    else:
        selected_feature_names = [f"feat_{i}" for i in range(X_train_sel.shape[1])]
        
    evaluator.plot_feature_importance(best_model, selected_feature_names, top_n=20)

    # 10. Save Artifacts
    artifact_mgr = ArtifactManager(artifact_dir='artifacts')
    artifact_mgr.save_artifacts(best_model, fe, selector, model_name=best_model_name)

    print("\n" + "="*70)
    print(" TRAINING PIPELINE SUCCESSFULLY COMPLETED ")
    print(" Artifacts saved to 'artifacts/' | Plots saved to 'plots/'")
    print("="*70)

if __name__ == "__main__":
    main()
