import json
import requests
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.http import HttpResponse
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity  
from tmdbv3api import TMDb, Movie


def get_movies_name():
    """
    To fetch titles of movies
    """
    # This file needs to be updated
    movies_df = pd.read_csv("pre_process/preProcessedDF.csv")
    # Return all movie titles and also make first letter of every word capital
    return movies_df['movie_title'].tolist()


# def import_to_db(request):


def home(request):
    """
    Home page
    :param request:
    Url: /movies/
    """
    # Get all available movie titles
    movie_titles_list = get_movies_name()

    # Convert list to json so we can easily pass it to JavaScript
    movie_titles = json.dumps(movie_titles_list)
    context = {'movie_titles': movie_titles}
    return render(request, 'home.html', context=context)


def get_movies(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        movies_df = pd.read_csv("pre_process/preProcessedDF.csv")
        filtered_df = movies_df.loc[movies_df["movie_title"].str.contains(q, case=False)]
        # places = Place.objects.filter(city__icontains=q)
        results = []
        # print(filtered_df)
        data = []
        count = 0;
        for index, row in filtered_df.iterrows():
            # To send only first 10 results
            if count > 10: break
            
            rep_json = {}
            # place_json = pl.city + "," + pl.state
            rep_json['id'] = row["movie_id"]
            # rep_json['movi'] = f'{item.rep_first_name} {item.rep_last_name}'
            rep_json['value'] = row["movie_title"]
            results.append(rep_json)
            count += 1
        data = json.dumps(results)
        # else:
        #     data = 'fail'
        
        # print(data)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)



def get_cast()
    cast_response = requests.get('https://api.themoviedb.org/3/movie/{}/credits?api_key={}'.format(movie_id,tmdb.api_key))
    
    if len(cast_response["cast"] >= 10):
        selected_cast_count = 10
    else:
        selected_cast_count = 5

    cast_names = []
    cast_chars = []
    for i in range(0, selected_cast_count):
        cast_names.append(cast_response["cast"][i]["name"])
        cast_chars.append(cast_response["cast"][i]["character"])




def recommend(request):
    """
    Get movie title from front end
    Verify if it is in our movie titles
    If yes then send details and recommended movies else not found message
    Url: /recommend?movie={movie_name}
    """
    if request.is_ajax():
        movie_id = request.GET.get('movie')
        movie_id = movie_id.strip()
        if not movie_id:
            response_data = {'movie_details': '', recommended_movies: ''}
            return HttpResponse(json.dumps(response_data, default=myconverter), content_type='application/json')
        else:
            # cosine_similarity = np.load('/home/triloq/stuff/projects/movie-recommendation-system/pre_process/similarity.npy')
            movies_df = pd.read_csv("pre_process/preProcessedDF.csv")
            

            cv = CountVectorizer()
            count_matrix = cv.fit_transform(movies_df['metadata'])
            print("Calculate count matrix")
            similarity = cosine_similarity(count_matrix)
            print("Calculate similarity matrix")
            # Fetch index in the DataFrame
            idx = movies_df.loc[movies_df['movie_id']==movie_id].index[0]
            lst = list(enumerate(similarity[idx]))
            lst = sorted(lst, key = lambda x:x[1], reverse=True)
            lst = lst[1:11] # excluding first item since it is the requested movie itself
            
            final_list = []
            for i in lst:
                inside_list = []
                inside_list.append(i[0])
                inside_list.append(i[1])
                inside_list.append(movies_df[movies_df.index == i[0]].iloc[0].movie_id)
                inside_list.append(movies_df[movies_df.index == i[0]].iloc[0].weighted_average)
                final_list.append(inside_list)

            print(final_list)
            # Sort based on weighted average
            sorted_lst = sorted(final_list, key = lambda x:x[3], reverse=True)
            print(sorted_lst)
            
            tmdb = TMDb()
            tmdb_movie = Movie()
            tmdb.api_key = '7c12036c11aea87af9d938d331e8c107'
            response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,tmdb.api_key))
            
            info_fetched = True
            movie_info = {}
            if response.status_code == 200:
               resp_json = response.json()
               movie_info["description"] = resp_json["overview"]
               movie_info["rating"] = resp_json["vote_average"]
               get_cast()

            else:
                info_fetched = False

            # return render(request, "recom.html", {"current_movie_id": movie_id, "sorted_lst": sorted_lst})
            # l = []
            # print(lst)
            # for i in range(len(lst)):
            #     a = lst[i][0]
            #     l.append(movies_df['movie_title'][a]) 
            # print(l)

            