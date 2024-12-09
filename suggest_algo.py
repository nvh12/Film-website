from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import requests
from tmdbv3api import TMDb, Movie
import sqlite3

# class for vectorizing the movie feature like actor1_name, director_name, genres
class TFIDFVectorizer:
    def __init__(self):
        self.vocab = {}
        self.idf_values = {}
    
    def fit(self, documents):
        # Create vocabulary and calculate document frequencies for each term
        doc_count = len(documents)
        doc_frequency = defaultdict(int)
        
        for doc in documents:
            tokens = self.tokenize(doc)
            unique_tokens = set(tokens)  # Only count each term once per document
            for token in unique_tokens:
                doc_frequency[token] += 1
        
        # Create vocabulary and compute IDF
        self.vocab = {term: idx for idx, term in enumerate(doc_frequency)}

        # Plus 1 for smoothing technique
        self.idf_values = {term: np.log(doc_count / (1 + doc_frequency[term])) for term in doc_frequency}

    def transform(self, documents):
        # Initialize TF-IDF matrix
        tfidf_matrix = np.zeros((len(documents), len(self.vocab)))
        
        for i, doc in enumerate(documents):
            tokens = self.tokenize(doc)
            term_counts = Counter(tokens)
            doc_length = len(tokens)
            
            for term, count in term_counts.items():
                if term in self.vocab:
                    tf = count / doc_length
                    idf = self.idf_values[term]
                    tfidf_matrix[i, self.vocab[term]] = tf * idf
        
        return tfidf_matrix

    def fit_transform(self, documents):
        self.fit(documents)
        return self.transform(documents)

    def tokenize(self, document):
        return document.split(", ")

class Suggestion:
    def distance(self, vector):
        return np.linalg.norm(vector)
    
    def get_suggestion(self, movie, movie_db, X, vectorizer):
        comb = movie['comb'].iloc[0]
        vector = vectorizer.transform([comb])[0]
        distances = []
        movieID = movie_db['movie_title']
        for i in movieID.index:
            distances.append([self.distance(X[i] - vector), movieID[i]])
        distances.sort()
        return [distances[i][1] for i in range(1,11)]

def suggest(title):
    conn = sqlite3.connect('instance/Database.db')
    query = "SELECT * FROM suggestion_table WHERE strftime('%Y', release_date) >= '2010'"
    movie_db = pd.read_sql_query(query, conn)
    movie = movie_db.query(f"movie_title == '{title}'")
    documents = movie_db['comb']
    tf_idf_vectorize = TFIDFVectorizer()
    tfidf_matrix = tf_idf_vectorize.fit_transform(documents)
    suggest = Suggestion()
    return suggest.get_suggestion(movie, movie_db, tfidf_matrix, tf_idf_vectorize)

print(suggest('Puss in Boots'))

