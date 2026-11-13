import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold
import xgboost as xgb

# Optional imports with fallbacks
try:
    import lightgbm as lgb
    HAS_LIGHTGBM = True
except ImportError:
    HAS_LIGHTGBM = False

try:
    import catboost as cb
    HAS_CATBOOST = True
except ImportError:
    HAS_CATBOOST = False

class ModelTrainer:
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.models = {}
        self.tuned_models = {}
        self.init_models()

    def init_models(self):
        self.models['Logistic Regression'] = LogisticRegression(max_iter=1000, random_state=self.random_state)
        self.models['Multinomial Naive Bayes'] = MultinomialNB()
        self.models['Linear SVM'] = LinearSVC(max_iter=2000, random_state=self.random_state, dual='auto')
        self.models['Random Forest'] = RandomForestClassifier(n_estimators=100, max_depth=20, random_state=self.random_state, n_jobs=-1)
        self.models['XGBoost'] = xgb.XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=self.random_state, n_jobs=-1, eval_metric='mlogloss')
        
        if HAS_LIGHTGBM:
            self.models['LightGBM'] = lgb.LGBMClassifier(n_estimators=100, random_state=self.random_state, n_jobs=-1, verbose=-1)
            
        if HAS_CATBOOST:
            self.models['CatBoost'] = cb.CatBoostClassifier(iterations=100, random_state=self.random_state, verbose=0)

    def train_all(self, X_train, y_train):
        trained_models = {}
        for name, model in self.models.items():
            print(f"Training {name}...")
            try:
                model.fit(X_train, y_train)
                trained_models[name] = model
            except Exception as e:
                print(f"[Warning] Training failed for {name}: {e}")
        return trained_models

    def tune_best_model(self, model_name, model, X_train, y_train, cv_folds=5, n_iter=10):
        print(f"\nTuning hyperparameters for {model_name}...")
        param_grids = {
            'Logistic Regression': {
                'C': [0.1, 1.0, 10.0],
                'solver': ['lbfgs', 'liblinear']
            },
            'Multinomial Naive Bayes': {
                'alpha': [0.01, 0.1, 0.5, 1.0]
            },
            'Linear SVM': {
                'C': [0.01, 0.1, 1.0, 10.0]
            },
            'Random Forest': {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5]
            },
            'XGBoost': {
                'n_estimators': [100, 200],
                'max_depth': [3, 6, 9],
                'learning_rate': [0.01, 0.1, 0.2]
            }
        }
        
        if HAS_LIGHTGBM:
            param_grids['LightGBM'] = {
                'n_estimators': [100, 200],
                'num_leaves': [31, 63],
                'learning_rate': [0.01, 0.1]
            }
            
        if HAS_CATBOOST:
            param_grids['CatBoost'] = {
                'iterations': [100, 200],
                'depth': [4, 6, 8],
                'learning_rate': [0.01, 0.1]
            }

        param_grid = param_grids.get(model_name, None)
        if not param_grid:
            print(f"No hyperparameter grid defined for {model_name}. Returning base model.")
            return model

        cv = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=self.random_state)
        search = RandomizedSearchCV(
            estimator=model,
            param_distributions=param_grid,
            n_iter=n_iter,
            scoring='f1_macro',
            cv=cv,
            random_state=self.random_state,
            n_jobs=-1
        )
        search.fit(X_train, y_train)
        print(f"Best Parameters for {model_name}: {search.best_params_}")
        print(f"Best CV Score: {search.best_score_:.4f}")
        return search.best_estimator_
