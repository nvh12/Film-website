from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import requests

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


# get the director_name, actor1_name, ... etc for the new movie input
class TMDB:
    def __init__(self):
        self.headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI5YTBhYmZkNTJiYjZjMjkwYzVjMTIzZDZiNjlkODNjYiIsIm5iZiI6MTcyOTM1MzA2NS44MTA5MTgsInN1YiI6IjY2ZjI3NWU0YTgyYjAwNTcwMzI2ZDIxZiIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.k1dQkNkB_2phSel35QLQSzoz98UoBve1fMRzHJyESKk"
        }

    def get_genres(self, movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
        response = requests.get(url, headers= self.headers)
        data = response.json()
        genres = ''
        for i in data['genres']:
            genres += i['name'] + ', '
        return genres[:-2]
    
    def get_director_cast(self, movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?language=en-US"
        response = requests.get(url, headers = self.headers)
        casts = response.json()['cast']
        director = response.json()['crew']
        actor1 = None 
        actor2 = None
        actor3 = None
        n = len(casts)
        if n >= 3:
            actor1, actor2, actor3 = [casts[i]['name'] for i in range(3)]
        else:
            actor1, actor2, actor3 = [casts[i]['name'] for i in range(n)] + [None * (3 - n)]
        director = director[0]['name']
        return actor1 + ', ' + actor2 + ', ' + actor3 + ', ' + director

from tmdbv3api import TMDb, Movie
tmdb = TMDb()
tmdb.api_key = '9a0abfd52bb6c290c5c123d6b69d83cb'
tmdb_movie = Movie()
TMDB  = TMDB()

class Suggestion:
    def distance(self, vector):
        return np.linalg.norm(vector)
    
    def get_suggestion(self, movie_title):
        result = tmdb_movie.search(movie_title)
        movie_id = result[0].id
        comb = (TMDB.get_director_cast(movie_id) +', '+ TMDB.get_genres(movie_id)).lower()
        print(comb)
        vector = tf_idf_vectorize.transform([comb])[0]
        distances = []
        movie = movie_db['title']
        for i in movie.index:
            distances.append([self.distance(X[i] - vector), movie[i]])
        distances.sort()
        return [distances[i][1] for i in range(1,11)]

tf_idf_vectorize = TFIDFVectorizer()

# replace 'file_name.csv' with a specific file

movie_db = pd.read_csv("'file_name'.csv")
movie_db.dropna(how = 'any', inplace=True)
movie_db.reset_index(drop = True, inplace = True)
def strip(feature):
    movie_db[feature] = movie_db[feature].apply(lambda x: x.strip())
strip_features = ['director_name','actor_1_name','actor_2_name','actor_3_name']
for i in strip_features:
    strip(i)
movie_db['comb'] = movie_db['actor_1_name'].str.lower() + ", " + movie_db['actor_2_name'].str.lower() + ", " + movie_db['actor_3_name'].str.lower() + ", " + movie_db['director_name'].str.lower() + ", " + movie_db['genres'].str.lower()

# vectorize the features
documents = movie_db['comb']
X = tf_idf_vectorize.fit_transform(documents)

# input the movie you want to suggest here
input_movie = ""
suggest = Suggestion()
suggested_movies = suggest.get_suggestion(input)
print(suggested_movies)