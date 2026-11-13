import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report,
    roc_curve, precision_recall_curve, auc
)
from sklearn.preprocessing import label_binarize

class Evaluator:
    def __init__(self, plot_dir='plots'):
        self.plot_dir = plot_dir
        os.makedirs(self.plot_dir, exist_ok=True)
        self.class_names = ['Ham', 'Spam', 'Phishing']

    def evaluate_model(self, model, X_train, y_train, X_test, y_test, model_name="Model"):
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        
        prec = precision_score(y_test, test_pred, average='macro', zero_division=0)
        rec = recall_score(y_test, test_pred, average='macro', zero_division=0)
        f1 = f1_score(y_test, test_pred, average='macro', zero_division=0)
        
        gap = train_acc - test_acc
        if train_acc < 0.80 and test_acc < 0.80:
            status = "Underfitting"
        elif gap > 0.05:
            status = "Overfitting"
        elif gap > 0.03:
            status = "Slight Overfit"
        else:
            status = "Optimal (Well-Fitted)"

        # Calculate ROC-AUC
        y_prob = None
        roc_auc = 0.0
        if hasattr(model, 'predict_proba'):
            try:
                y_prob = model.predict_proba(X_test)
                if len(np.unique(y_test)) > 2:
                    roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr', average='macro')
                else:
                    roc_auc = roc_auc_score(y_test, y_prob[:, 1])
            except Exception:
                roc_auc = 0.0
        elif hasattr(model, 'decision_function'):
            try:
                y_df = model.decision_function(X_test)
                if len(np.unique(y_test)) > 2 and y_df.ndim > 1:
                    roc_auc = roc_auc_score(y_test, y_df, multi_class='ovr', average='macro')
            except Exception:
                roc_auc = 0.0

        metrics = {
            'Model': model_name,
            'Train Accuracy': train_acc,
            'Test Accuracy': test_acc,
            'Accuracy Gap': gap,
            'Fit Status': status,
            'Precision': prec,
            'Recall': rec,
            'F1-Score': f1,
            'ROC-AUC': roc_auc
        }
        return metrics, test_pred, y_prob

    def compare_models(self, trained_models, X_train, y_train, X_test, y_test):
        results = []
        model_probs = {}
        model_preds = {}
        
        print("\n" + "="*75)
        print(" MODEL OVERFITTING / UNDERFITTING & ACCURACY EVALUATION ")
        print("="*75)
        
        for name, model in trained_models.items():
            m, test_pred, y_prob = self.evaluate_model(model, X_train, y_train, X_test, y_test, model_name=name)
            results.append(m)
            model_preds[name] = test_pred
            model_probs[name] = y_prob
            
            print(f"\n--- {name} ---")
            print(f"Training Accuracy: {m['Train Accuracy']:.4f} ({m['Train Accuracy']*100:.2f}%)")
            print(f"Testing Accuracy:  {m['Test Accuracy']:.4f} ({m['Test Accuracy']*100:.2f}%)")
            print(f"Accuracy Gap:      {m['Accuracy Gap']:+.4f} ({m['Accuracy Gap']*100:+.2f}%)")
            print(f"Generalization:    [{m['Fit Status']}]")
            print(f"Precision:         {m['Precision']:.4f}")
            print(f"Recall:            {m['Recall']:.4f}")
            print(f"F1-Score:          {m['F1-Score']:.4f}")
            print(f"ROC-AUC:           {m['ROC-AUC']:.4f}")
            print("\nTest Classification Report:")
            print(classification_report(y_test, test_pred, target_names=self.class_names[:len(np.unique(y_test))], zero_division=0))
            
        results_df = pd.DataFrame(results).sort_values(by='F1-Score', ascending=False).reset_index(drop=True)
        return results_df, model_preds, model_probs

    def plot_confusion_matrix(self, y_test, y_pred, model_name="Best Model"):
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(7, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    xticklabels=self.class_names[:cm.shape[1]],
                    yticklabels=self.class_names[:cm.shape[0]])
        plt.title(f'Confusion Matrix - {model_name}')
        plt.xlabel('Predicted Label')
        plt.ylabel('True Label')
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, 'confusion_matrix.png'), dpi=300)
        plt.close()

    def plot_roc_curves(self, y_test, y_prob, model_name="Best Model"):
        if y_prob is None:
            return
        
        n_classes = len(np.unique(y_test))
        y_test_bin = label_binarize(y_test, classes=list(range(n_classes)))
        
        plt.figure(figsize=(8, 6))
        colors = ['navy', 'turquoise', 'darkorange']
        
        for i in range(n_classes):
            if n_classes > 2:
                fpr, tpr, _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
                roc_auc = auc(fpr, tpr)
                class_label = self.class_names[i] if i < len(self.class_names) else f"Class {i}"
                plt.plot(fpr, tpr, color=colors[i % len(colors)], lw=2,
                         label=f'ROC curve {class_label} (AUC = {roc_auc:.2f})')
            else:
                fpr, tpr, _ = roc_curve(y_test, y_prob[:, 1])
                roc_auc = auc(fpr, tpr)
                plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
                break
                
        plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curves - {model_name}')
        plt.legend(loc="lower right")
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, 'roc_curves.png'), dpi=300)
        plt.close()

    def plot_precision_recall_curves(self, y_test, y_prob, model_name="Best Model"):
        if y_prob is None:
            return
            
        n_classes = len(np.unique(y_test))
        y_test_bin = label_binarize(y_test, classes=list(range(n_classes)))
        
        plt.figure(figsize=(8, 6))
        colors = ['teal', 'crimson', 'purple']
        
        for i in range(n_classes):
            if n_classes > 2:
                precision, recall, _ = precision_recall_curve(y_test_bin[:, i], y_prob[:, i])
                class_label = self.class_names[i] if i < len(self.class_names) else f"Class {i}"
                plt.plot(recall, precision, color=colors[i % len(colors)], lw=2,
                         label=f'P-R curve {class_label}')
            else:
                precision, recall, _ = precision_recall_curve(y_test, y_prob[:, 1])
                plt.plot(recall, precision, color='crimson', lw=2, label='P-R curve')
                break
                
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curves - {model_name}')
        plt.legend(loc="lower left")
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, 'precision_recall_curves.png'), dpi=300)
        plt.close()

    def plot_model_comparison(self, results_df):
        plt.figure(figsize=(12, 6))
        metrics_to_plot = ['Train Accuracy', 'Test Accuracy', 'Precision', 'Recall', 'F1-Score']
        df_melted = results_df.melt(id_vars=['Model'], value_vars=metrics_to_plot, var_name='Metric', value_name='Score')
        
        sns.barplot(data=df_melted, x='Model', y='Score', hue='Metric', palette='viridis')
        plt.ylim(0.0, 1.05)
        plt.title('Model Performance & Overfitting Comparison')
        plt.xticks(rotation=15)
        plt.tight_layout()
        plt.savefig(os.path.join(self.plot_dir, 'model_comparison.png'), dpi=300)
        plt.close()

    def plot_feature_importance(self, model, feature_names, top_n=20):
        plt.figure(figsize=(10, 8))
        importances = None
        
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            importances = np.mean(np.abs(model.coef_), axis=0) if model.coef_.ndim > 1 else np.abs(model.coef_[0])
            
        if importances is not None and len(importances) == len(feature_names):
            top_indices = np.argsort(importances)[::-1][:top_n]
            top_features = [feature_names[i] for i in top_indices]
            top_scores = importances[top_indices]
            
            sns.barplot(x=top_scores, y=top_features, hue=top_features, legend=False, palette='Blues_r')
            plt.title(f'Top {top_n} Most Discriminative Features')
            plt.xlabel('Importance / Weight Score')
            plt.tight_layout()
            plt.savefig(os.path.join(self.plot_dir, 'feature_importance.png'), dpi=300)
            plt.close()
            print(f"Top feature importances saved to plots/feature_importance.png")
