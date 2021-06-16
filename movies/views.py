import json
import pandas as pd
from django.shortcuts import render

def get_movies_name():
	"""
	To fetch titles of movies
	"""
	# This file needs to be updated
	movies_df = pd.read_csv("pre_process/output/content_filter_dataV1.csv")
	# Return all movie titles and also make first letter of every word capital
	return movies_df['movie_title'].str.title().tolist()


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
