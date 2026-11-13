import numpy as np
import scipy.sparse as sp
from sklearn.feature_selection import SelectKBest, chi2, f_classif
from sklearn.decomposition import TruncatedSVD

class FeatureSelector:
    def __init__(self, k=3000, score_func='chi2', use_pca=False, n_components=100):
        self.k = k
        self.score_func_name = score_func
        self.use_pca = use_pca
        self.n_components = n_components
        
        if score_func == 'chi2':
            self.selector = SelectKBest(score_func=chi2, k=k)
        else:
            self.selector = SelectKBest(score_func=f_classif, k=k)
            
        self.pca = TruncatedSVD(n_components=n_components, random_state=42) if use_pca else None
        self.selected_indices = None

    def fit_transform(self, X, y):
        # Ensure non-negative values for Chi2
        if self.score_func_name == 'chi2':
            if sp.issparse(X):
                X_pos = X.copy()
                X_pos.data = np.clip(X_pos.data, 0, None)
            else:
                X_pos = np.clip(X, 0, None)
        else:
            X_pos = X

        print(f"Selecting top {self.k} features using {self.score_func_name}...")
        k_actual = min(self.k, X_pos.shape[1])
        self.selector.k = k_actual
        X_selected = self.selector.fit_transform(X_pos, y)
        self.selected_indices = self.selector.get_support(indices=True)
        
        if self.use_pca:
            print(f"Applying TruncatedSVD/PCA reduction to {self.n_components} components...")
            X_selected = self.pca.fit_transform(X_selected)
            
        return X_selected

    def transform(self, X):
        if self.score_func_name == 'chi2':
            if sp.issparse(X):
                X_pos = X.copy()
                X_pos.data = np.clip(X_pos.data, 0, None)
            else:
                X_pos = np.clip(X, 0, None)
        else:
            X_pos = X

        X_selected = self.selector.transform(X_pos)
        if self.use_pca and self.pca is not None:
            X_selected = self.pca.transform(X_selected)
        return X_selected
