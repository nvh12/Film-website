from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import requests
from tmdbv3api import TMDb, Movie
import sqlite3

# class for vectorizing the movie feature like actor1_name, director_name, genres
class Onehotencoding:
    def __init__(self):
        self.vocab = {}
    
    def fit(self, documents):
        """
        Builds a vocabulary of unique terms from the given documents.
        """
        terms = set()  # Use a set to ensure unique terms across all documents
        
        for doc in documents:
            tokens = self.tokenize(doc)
            terms.update(tokens)  # Add all unique tokens from this document to the set
        
        # Create a mapping from term to index
        self.vocab = {term: idx for idx, term in enumerate(sorted(terms))}

    def transform(self, documents):
        """
        Transforms documents into a one-hot encoded matrix based on the vocabulary.
        """
        # Initialize a zero matrix for one-hot encoding
        ohe_matrix = np.zeros((len(documents), len(self.vocab)), dtype=int)
        
        for i, doc in enumerate(documents):
            tokens = self.tokenize(doc)
            unique_tokens = set(tokens)  # One-hot encoding only considers presence
            
            for term in unique_tokens:
                if term in self.vocab:
                    ohe_matrix[i, self.vocab[term]] = 1  # Mark presence as 1
        
        return ohe_matrix

    def fit_transform(self, documents):
        self.fit(documents)
        return self.transform(documents)

    def tokenize(self, document):
        return document.split(", ")

    def fit_transform(self, documents):
        self.fit(documents)
        return self.transform(documents)

    def tokenize(self, document):
        return document.split(", ")

class Suggestion:
    def get_suggestion(self, movie, movie_db, X, vectorizer):
        comb = movie['comb'].iloc[0]
        vector = vectorizer.transform([comb])[0]
        distances = []
        movieID = movie_db['movie_title']
        for i in movieID.index:
            distances.append([np.sum(np.bitwise_xor(X[i], vector)), movieID[i]])
        distances.sort()
        return [distances[i][1] for i in range(1,17)]

def suggest(title):
    conn = sqlite3.connect('instance/Database.db')
    query = "SELECT * FROM suggestion_table WHERE strftime('%Y', release_date) >= '2010'"
    target_query = f"SELECT * FROM suggestion_table WHERE movie_title = '{title}'"
    movie_db = pd.read_sql_query(query, conn)
    movie = pd.read_sql_query(target_query, conn)
    documents = movie_db['comb']
    ohe_vectorize = Onehotencoding()
    ohe_matrix = ohe_vectorize.fit_transform(documents)
    suggest = Suggestion()
    return suggest.get_suggestion(movie, movie_db, ohe_matrix, ohe_vectorize)



