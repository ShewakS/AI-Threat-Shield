import os
import re
import pandas as pd
import numpy as np

def clean_text(text):
    if not isinstance(text, str) or pd.isna(text):
        return ""
    # Strip basic HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Replace whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def find_dataset_file(rel_path):
    candidates = [
        rel_path,
        os.path.join('dataset', rel_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dataset', rel_path),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', rel_path),
        os.path.join('..', 'dataset', rel_path),
        os.path.join('backend', 'dataset', rel_path),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return rel_path

def load_sms_data(filepath='SMS Spam collection/spam.csv'):
    filepath = find_dataset_file(filepath)
    if not os.path.exists(filepath):
        print(f"[Warning] File not found: {filepath}")
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
    
    encodings = ['utf-8', 'latin-1', 'cp1252']
    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(filepath, encoding=enc)
            break
        except Exception:
            continue
            
    if df is None or 'v1' not in df.columns or 'v2' not in df.columns:
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    df = df[['v1', 'v2']].rename(columns={'v1': 'raw_label', 'v2': 'text'})
    df['text'] = df['text'].apply(clean_text)
    df = df[df['text'].str.len() > 3]
    
    # Map labels: ham -> 0, spam -> 1
    label_map = {'ham': 0, 'spam': 1}
    df['label'] = df['raw_label'].str.lower().map(label_map)
    df['data_type'] = 'text'
    return df[['text', 'label', 'data_type']].dropna()

def load_enron_data(filepath='Enron spam data/enron_spam_data.csv'):
    filepath = find_dataset_file(filepath)
    if not os.path.exists(filepath):
        print(f"[Warning] File not found: {filepath}")
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    try:
        df = pd.read_csv(filepath)
    except Exception:
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    df['Subject'] = df['Subject'].fillna('')
    df['Message'] = df['Message'].fillna('')
    df['text'] = (df['Subject'] + " " + df['Message']).apply(clean_text)
    df = df[df['text'].str.len() > 5]
    
    label_map = {'ham': 0, 'spam': 1}
    df['label'] = df['Spam/Ham'].str.lower().map(label_map)
    df['data_type'] = 'text'
    return df[['text', 'label', 'data_type']].dropna()

def load_phishing_email_data(filepath='phishing email/phishing_email.csv'):
    filepath = find_dataset_file(filepath)
    if not os.path.exists(filepath):
        print(f"[Warning] File not found: {filepath}")
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    try:
        df = pd.read_csv(filepath)
    except Exception:
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    if 'text_combined' not in df.columns or 'label' not in df.columns:
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    df['text'] = df['text_combined'].apply(clean_text)
    df = df[df['text'].str.len() > 5]
    # In phishing_email dataset: 0 = Ham, 1 = Phishing (2)
    df['label'] = df['label'].map({0: 0, 1: 2})
    df['data_type'] = 'text'
    return df[['text', 'label', 'data_type']].dropna()

def load_malicious_url_data(filepath='Malicious URL/malicious_phish.csv'):
    filepath = find_dataset_file(filepath)
    if not os.path.exists(filepath):
        print(f"[Warning] File not found: {filepath}")
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    try:
        df = pd.read_csv(filepath)
    except Exception:
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    if 'url' not in df.columns or 'type' not in df.columns:
        return pd.DataFrame(columns=['text', 'label', 'data_type'])
        
    df = df.rename(columns={'url': 'text', 'type': 'raw_type'})
    df['text'] = df['text'].astype(str).str.strip()
    
    # Map benign -> 0 (Ham), phishing/malware/defacement -> 2 (Phishing)
    url_label_map = {
        'benign': 0,
        'phishing': 2,
        'malware': 2,
        'defacement': 2
    }
    df['label'] = df['raw_type'].str.lower().map(url_label_map)
    df['data_type'] = 'url'
    return df[['text', 'label', 'data_type']].dropna()

def load_and_preprocess_dataset(sample_size=None, random_state=42):
    """
    Merges all available datasets into a single standardized dataframe.
    Target classes:
      0: Ham (Legitimate)
      1: Spam (Unsolicited Commercial)
      2: Phishing (Malicious / Credential Harvester)
    """
    print("Loading datasets...")
    dfs = []
    
    df_sms = load_sms_data()
    if len(df_sms) > 0:
        print(f"Loaded SMS Spam data: {len(df_sms)} rows")
        dfs.append(df_sms)
        
    df_enron = load_enron_data()
    if len(df_enron) > 0:
        print(f"Loaded Enron Email data: {len(df_enron)} rows")
        dfs.append(df_enron)
        
    df_phish_email = load_phishing_email_data()
    if len(df_phish_email) > 0:
        print(f"Loaded Phishing Email data: {len(df_phish_email)} rows")
        dfs.append(df_phish_email)
        
    df_url = load_malicious_url_data()
    if len(df_url) > 0:
        print(f"Loaded Malicious URL data: {len(df_url)} rows")
        dfs.append(df_url)
        
    if not dfs:
        raise ValueError("No dataset files found!")
        
    combined_df = pd.concat(dfs, ignore_index=True)
    combined_df['label'] = combined_df['label'].astype(int)
    
    # Remove duplicate texts
    combined_df = combined_df.drop_duplicates(subset=['text']).reset_index(drop=True)
    
    # Balanced sampling across present classes
    if sample_size is not None and len(combined_df) > sample_size:
        unique_labels = combined_df['label'].unique()
        per_class_limit = max(sample_size // len(unique_labels), 100)
        print(f"Balanced sampling up to {per_class_limit} records per class...")
        
        sampled_dfs = []
        for lbl in unique_labels:
            sub_df = combined_df[combined_df['label'] == lbl]
            n_samples = min(len(sub_df), per_class_limit)
            sampled_dfs.append(sub_df.sample(n=n_samples, random_state=random_state))
            
        combined_df = pd.concat(sampled_dfs, ignore_index=True).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
        
    print("\nDataset Summary:")
    print(f"Total Samples: {len(combined_df)}")
    print(f"Class Distribution (0:Ham, 1:Spam, 2:Phishing): {combined_df['label'].value_counts().to_dict()}")
    print(f"Missing Values: {combined_df.isnull().sum().to_dict()}")
    
    return combined_df
