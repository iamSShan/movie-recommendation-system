import ast
import pandas as pd
import numpy as np
import json
import requests
from tmdbv3api import TMDb, Movie


def process_till_2016():
    print("###############################################################################")
    # In this file we have data till 2016
    df = pd.read_csv("data/movie_metadata.csv")

    print("Shape of dataset: {}\n".format(df.shape))
    print("Columns in dataset: {}".format(df.columns))

    # Select all rows and only specific columns:
    df = df.loc[:,["movie_title", "director_name", "actor_1_name", "actor_2_name", "actor_3_name", "genres"]]  

    # print(df.movie_title[0][-1])
    # Last character of name contains `\xa0` character so remove it after converting it to lower case
    df["movie_title"] = df["movie_title"].str.lower().apply(lambda i: i[:-1])
    df["actor_1_name"] = df["actor_1_name"].replace(np.nan, "unknown")
    df["actor_2_name"] = df["actor_2_name"].replace(np.nan, "unknown")
    df["actor_3_name"] = df["actor_3_name"].replace(np.nan, "unknown")
    df["director_name"] = df["director_name"].replace(np.nan, "unknown")
    df["genres"] = df["genres"].replace('|', ' ')
    df['all'] = df['actor_1_name'] + ' ' + df['actor_2_name'] + ' '+ df['actor_3_name'] + ' '+ df['director_name'] +' ' + df['genres']
    return df


def get_genres_list(the_list):
    """
    From list of dictionaries get only genres names

    """
    genres_list = []
    for i in the_list:
        if i.get("name") == "Science Fiction":
            scifi = "Sci-Fi"
            genres_list.append("Sci-Fi")
        else:
            genres_list.append(i.get("name"))
    if genres_list == []:
        return np.NaN
    else:
        genres_list = list(set(genres_list))
        return (" ".join(genres_list))


def get_actor1(x):
    casts = []
    for i in x:
        casts.append(i.get('name'))
    if casts == []:
        return np.NaN
    else:
        return (casts[0])


def get_actor2(x):
    casts = []
    for i in x:
        casts.append(i.get('name'))
    # We have to also check whether 2nd actor info is present or not
    if casts == [] or len(casts)<=1:
        return np.NaN
    else:
        return (casts[1])


def get_actor3(x):
    casts = []
    for i in x:
        casts.append(i.get('name'))
    # We have to also check whether 3rd actor info is present or not
    if casts == [] or len(casts)<=2:
        return np.NaN
    else:
        return (casts[2])


def get_directors(x):
    dt = []
    for i in x:
        if i.get('job') == 'Director':
            dt.append(i.get('name'))
    if dt == []:
        return np.NaN
    else:
        return " ".join(dt)


def process_for_2017(df_2016):
    # Now we can to append with a data where we have 2017 data also available
    print("###############################################################################")
    credits_df = pd.read_csv("data/credits.csv")
    print("\nShape of credits dataset: {}\n".format(credits_df.shape))
    print("Columns in credits dataset: {}".format(credits_df.columns))
    print(credits_df.head())
    print(credits_df.dtypes)

    print("###############################################################################")
    meta_df = pd.read_csv("data/movies_metadata.csv")
    print("\nShape of movies meta dataset: {}\n".format(meta_df.shape))
    print("Columns in movies meta dataset: {}".format(meta_df.columns))
    print(meta_df.head())

    print(meta_df["release_date"])
    # use errors="coerce", else you can get error: `ValueError: Given date string not likely a datetime.`
    meta_df["release_date"] = pd.to_datetime(meta_df['release_date'], errors="coerce")
    # If ‘coerce’, then invalid parsing will be set as NaN.
    # print(meta_df["release_date"])
    # Just get the year from date and show counts of values using 
    meta_df["year"] = meta_df["release_date"].dt.year
    # print(meta_df["year"].dt.year.value_counts().sort_index())

    # Now for year 2017
    # Select only those rows having year value as 2017 and select only required columns
    meta_2017 = meta_df.loc[meta_df.year == 2017, ["id", "title", "genres", "year"]]

    print(meta_2017.dtypes)
    # Now change id column from object(str or mixed) to integer
    meta_2017["id"] = meta_2017["id"].astype("int")

    # Credits DF `id` column is already in integer
    # Now join credit and meta DF
    df_2017 = pd.merge(meta_2017, credits_df, on="id")

    # print(df_2017["genres"])
    # Column type of genres, cast, and crew are string representation of list, we need to convert first them to list
    # print(df_2017["genres"])
    df_2017["genres"] = df_2017["genres"].map(lambda x: ast.literal_eval(x))
    df_2017["cast"] = df_2017["cast"].map(lambda x: ast.literal_eval(x))
    df_2017["crew"] = df_2017["crew"].map(lambda x: ast.literal_eval(x))

    # Process for genres
    df_2017["genres_list"] = df_2017["genres"].map(lambda x : get_genres_list(x))    
    print(df_2017["genres_list"])
    # Now get all actors
    df_2017['actor_1_name'] = df_2017['cast'].map(lambda x: get_actor1(x))
    df_2017['actor_2_name'] = df_2017['cast'].map(lambda x: get_actor2(x))
    df_2017['actor_3_name'] = df_2017['cast'].map(lambda x: get_actor3(x))
    # Now for the directors
    df_2017['director_name'] = df_2017['crew'].map(lambda x: get_directors(x))
    # print(df_2017['director_name'])
    # Now filter some specific columns
    df_2017 = df_2017.loc[:,['director_name','actor_1_name','actor_2_name','actor_3_name','genres_list','title']]
    # Now check how many missing values are there
    print("Missing values:\n{}".format(df_2017.isna().sum()))
    # Now drop missing values
    """
    dropna:
    ‘any’ : If any NA values are present, drop that row or column.
    ‘all’ : If all values are NA, drop that row or column.
    """
    df_2017 = df_2017.dropna(how="any")
    # Now we have to rename the columns wrt to df_2016.  
    df_2017 = df_2017.rename(columns={'genres_list':'genres'})
    df_2017 = df_2017.rename(columns={'title':'movie_title'})
    print(df_2017.shape)
    df_2017['movie_title'] = df_2017['movie_title'].str.lower()
    # Combine all the cast crew and genres to create a new column which can be further processed using NLP
    df_2017['all'] = df_2017['actor_1_name'] + ' ' + df_2017['actor_2_name'] + ' '+ df_2017['actor_3_name'] + ' '+ df_2017['director_name'] +' ' + df_2017['genres']
    print(df_2016.columns)
    # Now combine with dataset having till 2016 data
    movie_df = df_2016.append(df_2017)
    print("Shape of combined dataset: {}".format(movie_df.shape))
    # Now drop duplicates if any
    movie_df.drop_duplicates(subset="movie_title", keep="last", inplace=True)
    print("Shape of final dataset till 2017: {}".format(movie_df.shape))
    return movie_df


def get_2018_movies(df_till_2017):
    link = "https://en.wikipedia.org/wiki/List_of_American_films_of_2018"
    df1 = pd.read_html(link, header=0)[2]
    df2 = pd.read_html(link, header=0)[3]
    df3 = pd.read_html(link, header=0)[4]
    df4 = pd.read_html(link, header=0)[5]
    df = df1.append(df2.append(df3.append(df4,ignore_index=True),ignore_index=True),ignore_index=True)

    tmdb = TMDb()
    tmdb_movie = Movie()
    tmdb.api_key = '7c12036c11aea87af9d938d331e8c107'
    def get_genre(x):
        genres = []
        result = tmdb_movie.search(x)
        movie_id = result[0].id
        response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,tmdb.api_key))
        resp_json = response.json()
        if resp_json['genres']:
            for i in range(0, len(resp_json['genres'])):
                genres.append(resp_json['genres'][i]['name'])
            return " ".join(genres)
        else:
            np.NaN
    print("Getting genres....")
    df["genres"] = df["Title"].map(lambda x: get_genre(str(x)))
    print(df.columns)
    # df_2019 = df[['Title','Cast and crew','Genre']]


if __name__ == "__main__":
    # df_till_2016 = process_till_2016()
    # df_till_2017 = process_for_2017(df_2016)
    get_2018_movies(df_till_2017=[])