import re
import string
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import nltk

# Ensure required NLTK packages are downloaded
for resource in ['punkt', 'punkt_tab', 'averaged_perceptron_tagger', 'vader_lexicon', 'stopwords']:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk import pos_tag, word_tokenize

SUSPICIOUS_KEYWORDS = [
    'login', 'update', 'bank', 'verify', 'account', 'secure', 'click', 'win',
    'free', 'claim', 'paypal', 'ebay', 'signin', 'admin', 'webscr', 'password',
    'security', 'confirm', 'urgent', 'limited', 'offer', 'alert', 'action',
    'service', 'access', 'blocked', 'suspended', 'immediately'
]

class FeatureEngineer:
    def __init__(self, max_tfidf_features=5000):
        self.max_tfidf_features = max_tfidf_features
        self.tfidf_vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=max_tfidf_features,
            stop_words='english',
            sublinear_tf=True
        )
        self.scaler = StandardScaler()
        self.vader = SentimentIntensityAnalyzer()
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = set()
        self.feature_names = []

    def extract_url_features(self, text_series):
        features = []
        for text in text_series:
            text_str = str(text)
            url_len = len(text_str)
            has_https = 1 if 'https://' in text_str.lower() else 0
            dot_count = text_str.count('.')
            digit_count = sum(c.isdigit() for c in text_str)
            hyphen_count = text_str.count('-')
            slash_count = text_str.count('/')
            special_char_count = sum(1 for c in text_str if c in "@?=%&_~")
            suspicious_kw_count = sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in text_str.lower())
            
            features.append([
                url_len, has_https, dot_count, digit_count, hyphen_count,
                slash_count, special_char_count, suspicious_kw_count
            ])
        
        feature_names = [
            'url_len', 'has_https', 'dot_count', 'digit_count', 'hyphen_count',
            'slash_count', 'special_char_count', 'suspicious_kw_count'
        ]
        return np.array(features), feature_names

    def extract_statistical_features(self, text_series):
        features = []
        for text in text_series:
            text_str = str(text)
            char_count = len(text_str)
            words = text_str.split()
            word_count = len(words)
            upper_char_count = sum(1 for c in text_str if c.isupper())
            upper_char_ratio = upper_char_count / (char_count + 1e-5)
            punct_count = sum(1 for c in text_str if c in string.punctuation)
            punct_ratio = punct_count / (char_count + 1e-5)
            digit_count = sum(1 for c in text_str if c.isdigit())
            digit_ratio = digit_count / (char_count + 1e-5)
            upper_word_count = sum(1 for w in words if w.isupper() and len(w) > 1)
            upper_word_ratio = upper_word_count / (word_count + 1e-5)
            
            features.append([
                word_count, char_count, upper_char_ratio, punct_count,
                punct_ratio, digit_ratio, upper_word_ratio
            ])
            
        feature_names = [
            'word_count', 'char_count', 'upper_char_ratio', 'punct_count',
            'punct_ratio', 'digit_ratio', 'upper_word_ratio'
        ]
        return np.array(features), feature_names

    def extract_linguistic_and_sentiment_features(self, text_series):
        features = []
        for text in text_series:
            text_str = str(text)
            
            # Sentiment scores
            try:
                sent = self.vader.polarity_scores(text_str)
                compound = sent['compound']
                pos_score = sent['pos']
                neg_score = sent['neg']
            except Exception:
                compound, pos_score, neg_score = 0.0, 0.0, 0.0
                
            # Basic POS tagging sample
            tokens = text_str.split()[:50] # truncated for speed
            words_len = len(tokens) + 1e-5
            stopword_count = sum(1 for w in tokens if w.lower() in self.stop_words)
            stopword_ratio = stopword_count / words_len
            
            avg_word_len = sum(len(w) for w in tokens) / words_len
            
            features.append([
                compound, pos_score, neg_score, stopword_ratio, avg_word_len
            ])
            
        feature_names = [
            'sentiment_compound', 'sentiment_pos', 'sentiment_neg',
            'stopword_ratio', 'avg_word_len'
        ]
        return np.array(features), feature_names

    def fit_transform(self, df):
        texts = df['text'].fillna('').astype(str)
        
        print("Extracting TF-IDF features...")
        tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
        tfidf_feature_names = [f"tfidf_{name}" for name in self.tfidf_vectorizer.get_feature_names_out()]
        
        print("Extracting URL features...")
        url_feats, url_names = self.extract_url_features(texts)
        
        print("Extracting statistical features...")
        stat_feats, stat_names = self.extract_statistical_features(texts)
        
        print("Extracting linguistic and sentiment features...")
        ling_feats, ling_names = self.extract_linguistic_and_sentiment_features(texts)
        
        dense_features = np.hstack([url_feats, stat_feats, ling_feats])
        scaled_dense_features = self.scaler.fit_transform(dense_features)
        
        self.feature_names = tfidf_feature_names + url_names + stat_names + ling_names
        
        combined_matrix = sp.hstack([tfidf_matrix, sp.csr_matrix(scaled_dense_features)], format='csr')
        return combined_matrix

    def transform(self, df):
        texts = df['text'].fillna('').astype(str)
        tfidf_matrix = self.tfidf_vectorizer.transform(texts)
        
        url_feats, _ = self.extract_url_features(texts)
        stat_feats, _ = self.extract_statistical_features(texts)
        ling_feats, _ = self.extract_linguistic_and_sentiment_features(texts)
        
        dense_features = np.hstack([url_feats, stat_feats, ling_feats])
        scaled_dense_features = self.scaler.transform(dense_features)
        
        combined_matrix = sp.hstack([tfidf_matrix, sp.csr_matrix(scaled_dense_features)], format='csr')
        return combined_matrix
