import json
import requests
import requests_cache
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity  
from tmdbv3api import TMDb, Movie


# This will cache the response fetched using requests library and store it inside cache folder
requests_cache.install_cache('cache/movies_cache', backend='sqlite')


def home(request):
    """
    Home page
    :param request:
    Url: /movies/
    """
    return render(request, 'home.html', context={})


def get_movies(request):
    """
    When user enters in search box this function is called
    :param request:
    """
    if request.is_ajax():
        # Get entered letter from front end
        query = request.GET.get('term', '')
        # Read pandas file and search all rows with movie title similar to that searched term
        movies_df = pd.read_csv("pre_process/preProcessedDF.csv")
        filtered_df = movies_df.loc[movies_df["movie_title"].str.contains(query, case=False)]

        results = []
        # Count will store how many results we are going to return, right now it is 10
        count = 0
        for index, row in filtered_df.iterrows():
            # To send only first 10 results
            if count > 10:
                break

            # Dictionary to store movie id and movie title for each movie
            rep_json = {}
            rep_json['id'] = row["movie_id"]
            rep_json['value'] = row["movie_title"]
            results.append(rep_json)
            count += 1

        # Dump results to json and return it as response
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


def get_cast(movie_id, tmdb):
    """
    To return cast using API call for a given movie id
    :param movie_id: Unique Id for a movie
    :param tmdb: TMDB API object

    :return: dictionary containing cast details
    """

    # Fetch data from url and API key
    cast_response = requests.get('https://api.themoviedb.org/3/movie/{}/credits?api_key={}'.format(movie_id,tmdb.api_key))
    # cast_response = requests.get('https://api.themoviedb.org/3/movie/{}/credits?api_key={}'.format(movie_id,tmdb.api_key), timeout=0.5)
    # Convert response to json
    resp_json = cast_response.json()
    
    # Select only limited number of cast
    if len(resp_json["cast"]) >= 10:
        selected_cast_count = 10
    else:
        selected_cast_count = 5

    cast = {}
    cast_profile = ''

    # For selected cast count, inside a dictionary store actor name, actor's character name and actor's image url
    for i in range(0, selected_cast_count):

        if resp_json["cast"][i]["profile_path"]:
            # Add url of cast image
            cast_profile = "https://image.tmdb.org/t/p/original"+resp_json["cast"][i]["profile_path"]
        else:
            # We will add `Image not available` image if any cast photo is not available in API response
            cast_profile = "https://westsiderc.org/wp-content/uploads/2019/08/Image-Not-Available.png"

        cast[resp_json["cast"][i]["name"]] = [resp_json["cast"][i]["character"], cast_profile]
        
    return cast


def get_recommended_movies(movies, tmdb):
    """
    Get recommended movies info using API
    """
    recommended_movies = {}
    for idx, movie_list in enumerate(movies):
        # We will just fetch 8 recommended movies response
        if idx > 7:
            break
        movie_id = movie_list[2]
        response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id, tmdb.api_key))
        # response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id, tmdb.api_key), timeout=0.5)
        resp = response.json()

        # Store movie_id, movie_title, movie poster image url in a dictionary
        imdb_id = resp["imdb_id"]
        title = resp["title"]
        poster_path = "https://image.tmdb.org/t/p/original"+resp["poster_path"]
        recommended_movies[imdb_id] = [title, poster_path]

    return recommended_movies


def recommend(request):
    """
    Get movie title from front end
    Verify if it is in our movie titles
    If yes then send details and recommended movies else not found message
    Url: /recommend?movie={movie_name}
    """
    if request.is_ajax():
        # Get movie id from front end for which recommendation needs to be fetched
        movie_id = request.GET.get('movie')
        movie_id = movie_id.strip()
        print(movie_id)

        # If no movie id is received from front end then return empty response
        if not movie_id:
            response_data = {'movie_details': '', recommended_movies: ''}
            return HttpResponse(json.dumps(response_data, default=myconverter), content_type='application/json')

        else:
            # Read the csv file containing list of movies
            movies_df = pd.read_csv("pre_process/preProcessedDF.csv")

            # Get some movie info from csv file for given movie id
            movie_title = movies_df.loc[movies_df.movie_id == movie_id, "movie_title"].item()
            description = movies_df.loc[movies_df.movie_id == movie_id, "description"].item()
            genre = movies_df.loc[movies_df.movie_id == movie_id, "genre"].item()
            rating = round(movies_df.loc[movies_df.movie_id == movie_id, "weighted_average"].item(), 2)
            year = int(movies_df.loc[movies_df.movie_id == movie_id, "year"].item())
            duration = movies_df.loc[movies_df.movie_id == movie_id, "duration"].item()
            director = movies_df.loc[movies_df.movie_id == movie_id, "director"].item()

            # We will only recommend those movies for which number of votes are greater than 2000 and weighted_average > 3 to improve recommendations
            # Also we won't apply this logic to year 2020, as dataset was created in 2020, so movies released in 2020 might not have big number of votes
            movies_df = movies_df.loc[((movies_df['votes']>=2000) & (movies_df['year'] < 2020) & (movies_df["weighted_average"] > 3)) | (movies_df['year'] == 2020) | (movies_df['movie_id'] == movie_id)]
            movies_df.reset_index(drop=True, inplace=True)

            # CountVectorizer converts a collection of text documents to a matrix of token counts: the occurrences of tokens in each document.
            # It results in a sparse representation of the counts.
            cv = CountVectorizer()
            count_matrix = cv.fit_transform(movies_df['metadata'])
            print("Created count matrix")

            # Using cosine similarity to create score matrix
            similarity = cosine_similarity(count_matrix)
            print("Calculated similarity matrix")
            
            # Fetch index in the DataFrame
            idx = movies_df.loc[movies_df['movie_id'] == movie_id].index[0]
            # We will get movies which have highest similarity
            movie_list = list(enumerate(similarity[idx]))
            movie_list = sorted(movie_list, key = lambda x:x[1], reverse=True)
            movie_list = movie_list[1:9]  # Excluding first item since it is the requested movie itself
            
            # Adding movie_id and weighted average for each movie
            final_list = []
            for i in movie_list:
                inside_list = []
                inside_list.append(i[0])
                inside_list.append(i[1])
                inside_list.append(movies_df[movies_df.index == i[0]].iloc[0].movie_id)
                inside_list.append(movies_df[movies_df.index == i[0]].iloc[0].weighted_average)
                final_list.append(inside_list)

            # Sorting the list based on weighted average
            sorted_lst = sorted(final_list, key = lambda x:x[3], reverse=True)
            
            # Calling API
            tmdb = TMDb()
            tmdb_movie = Movie()
            tmdb.api_key = ''
            print("Getting response here")
            response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id,tmdb.api_key))
            # response = requests.get("https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id,tmdb.api_key), timeout=0.5)
            print("Got response data here")
            info_fetched = True
            movie_info = {}
            cast_names, cast_chars, cast_profile = [], [], []
            if response.status_code == 200:
               resp_json = response.json()
               # movie_info["description"] = resp_json["overview"]
               movie_info["rating"] = resp_json["vote_average"]
               movie_info["poster"] = "https://image.tmdb.org/t/p/original"+resp_json["poster_path"]
               print("Getting cast")
               cast = get_cast(movie_id, tmdb)

            else:
                info_fetched = False
            
            # Get Recommended movies: movie_id, movie_title, movie_logo
            print("Getting recommended movies")
            recommended_movies = get_recommended_movies(sorted_lst, tmdb)

            # https://api.themoviedb.org/3/movie/tt0080684?api_key=
            # https://api.themoviedb.org/3/movie/tt0080684/credits?api_key=


            return render(request, "recom.html", {"movie_id": movie_id, "movie_info": movie_info, "movie_title": movie_title,
            "description": description, "genre": genre, "rating": rating, "year": year, "duration": duration, "director": director,
            "cast_info": cast.items(), "recommended_movies": recommended_movies.items()})