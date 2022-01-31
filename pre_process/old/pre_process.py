# This data pre process step has be referred from some open source code which was available on GitHub.

import ast
import pandas as pd
import numpy as np
import json
import requests
import requests_cache

from tmdbv3api import TMDb, Movie
import tmdbsimple as tmdb_simple  # Using this because tmdbv3api doesn't provides any other parameter while searching; like we have to search a common movie name like `raid` then multiple results can come.


requests_cache.install_cache('cache/2018_cache', backend='sqlite')

def process_till_2016():
    print("###############################################################################")
    # In this file we have data till 2016
    print("Processing for 2016...")
    df = pd.read_csv("pre_process/data/movie_metadata.csv")

    print("Shape of dataset: {}\n".format(df.shape))
    print("Columns in dataset: {}".format(df.columns))
    print(df["imdb_score"])

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
    df['metadata'] = df['actor_1_name'] + ' ' + df['actor_2_name'] + ' '+ df['actor_3_name'] + ' '+ df['director_name'] +' ' + df['genres']
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
    # Now we can append with the data where we have 2017 data also available
    print("###############################################################################")
    print("Processing for 2017...")
    credits_df = pd.read_csv("pre_process/data/movies_dataset/credits.csv")
    print("\nShape of credits dataset: {}\n".format(credits_df.shape))
    print("Columns in credits dataset: {}".format(credits_df.columns))
    print(credits_df.head())
    print(credits_df.dtypes)

    print("###############################################################################")
    meta_df = pd.read_csv("pre_process/data/movies_dataset/movies_metadata.csv")
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
    df_2017['metadata'] = df_2017['actor_1_name'] + ' ' + df_2017['actor_2_name'] + ' '+ df_2017['actor_3_name'] + ' '+ df_2017['director_name'] +' ' + df_2017['genres']
    print(df_2016.columns)
    # Now combine with dataset having till 2016 data
    movie_df = df_2016.append(df_2017)
    print("Shape of combined dataset: {}".format(movie_df.shape))
    # Now drop duplicates if any
    movie_df.drop_duplicates(subset="movie_title", keep="last", inplace=True)
    print("Shape of final dataset till 2017: {}".format(movie_df.shape))
    return movie_df


def process_wiki_movies(link, wiki_table_indexes, year):
    print("## Reading link: {}".format(link))
    df1 = pd.read_html(link, header=0)[wiki_table_indexes[0]]
    df2 = pd.read_html(link, header=0)[wiki_table_indexes[1]]

    df3 = pd.read_html(link, header=0)[wiki_table_indexes[2]]
    df4 = pd.read_html(link, header=0)[wiki_table_indexes[3]]
    # print(df1['Cast'])
    df = df1.append(df2.append(df3.append(df4,ignore_index=True),ignore_index=True),ignore_index=True)
    
    # print(df["Cast"][0].split())
    # Rename 'Cast and crew' to 'Cast' to generalize it for both Bollywood and Hollywood movies
    if 'Cast and crew' in df.columns:
        df = df.rename(columns={'Cast and crew': 'Cast'})

    
    # else:
    #     df = df1.append(df2, ignore_index=True)

    tmdb = TMDb()
    # if "Bollywood" in link:
    #     tmdb.language = 'en'
    #     tmdb.debug = True
    tmdb_movie = Movie()
    tmdb.api_key = '7c12036c11aea87af9d938d331e8c107'
    tmdb_simple.API_KEY = '7c12036c11aea87af9d938d331e8c107'

    def get_holly_genre(x):
        genres = []
        result = tmdb_movie.search(x)
        if not result:
            print("Movie genre not found: {}".format(x))
            return None
        movie_id = result[0].id
        response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,tmdb.api_key))
        resp_json = response.json()

        if resp_json['genres']:
            for i in range(0, len(resp_json['genres'])):
                genres.append(resp_json['genres'][i]['name'])
            return " ".join(genres)
        else:
            np.NaN


    def get_bolly_genre(x):
        genres = []
        search = tmdb_simple.Search()
        search_result = search.movie(query=x, year=year)
        if not search_result or not search_result['results']:
            print("Movie genre not found: {}".format(x))
            return None
        movie_id = search_result["results"][0]["id"]
        response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key={}'.format(movie_id,tmdb.api_key))
        resp_json = response.json()

        if resp_json['genres']:
            for i in range(0, len(resp_json['genres'])):
                genres.append(resp_json['genres'][i]['name'])
            return " ".join(genres)
        else:
            np.NaN


    def get_actors_for_bolly(x):
        """
        As from wikipedia read_html, actors are not fetched without spaces; names are getting mixed
        """
        x = str(x)
        import sys
        cast = []
        search = tmdb_simple.Search()
        search_result = search.movie(query=x, year=year)
        if not search_result or not search_result['results']:
            print("Movie cast not found: {}".format(x))
            return None, None, None

        movie_id = search_result["results"][0]["id"]
        response = requests.get('https://api.themoviedb.org/3/movie/{}/credits?api_key={}&region=IN&language=hi'.format(movie_id,tmdb.api_key))
        resp_json = response.json()
        # print(resp_json1['cast'])

        if resp_json['cast']:
            for i in range(0, len(resp_json['cast'])):
                cast.append(resp_json['cast'][i]['name'])
            # print(resp_json['cast'])
            if len(cast) >=3 :
                return cast[0], cast[1], cast[2]
            elif len(cast) == 2:
                return cast[0], cast[1], None
            else:
                return cast[0], None, None
        else:
            return np.NaN, np.NaN, np.NaN 


    def get_director_wiki(x):
        if " (director)" in x:
            return x.split(" (director)")[0]
        elif " (directors)" in x:
            return x.split(" (directors)")[0]
        else:
            return x.split(" (director/screenplay)")[0]

    def get_actor1_wiki(x):
        return ((x.split("screenplay)  ")[-1]).split(", ")[0])
    
    def get_actor2_wiki(x):
        if len((x.split("screenplay)  ")[-1]).split(", ")) < 2:
            return np.NaN
        else:
            return ((x.split("screenplay)  ")[-1]).split(", ")[1])

    def get_actor3_wiki(x):
        if len((x.split("screenplay)  ")[-1]).split(", ")) < 3:
            return np.NaN
        else:
            return ((x.split("screenplay)  ")[-1]).split(", ")[2])

    print("Getting genres....")
    if "Bollywood" in link:
        df["genres"] = df["Title"].map(lambda x: get_bolly_genre(str(x)))
    else:
        df["genres"] = df["Title"].map(lambda x: get_holly_genre(str(x)))

    # Fetch only required columns
    df = df[['Title','Cast','genres']]
    df['director_name'] = df['Cast'].map(lambda x: get_director_wiki(str(x)))  

    if "Bollywood" in link:
        df['actor_1_name'],  df['actor_2_name'], df['actor_3_name'] = zip(*df["Title"].map(lambda x: get_actors_for_bolly(str(x))))
    else:
        df['actor_1_name'] = df['Cast'].map(lambda x: get_actor1_wiki(str(x)))
        df['actor_2_name'] = df['Cast'].map(lambda x: get_actor2_wiki(str(x)))
        df['actor_3_name'] = df['Cast'].map(lambda x: get_actor3_wiki(str(x)))
    df = df.rename(columns={'Title':'movie_title'})
    df = df.loc[:,['director_name','actor_1_name','actor_2_name','actor_3_name','genres','movie_title']]
    df['actor_2_name'] = df['actor_2_name'].replace(np.nan, 'unknown')
    df['actor_3_name'] = df['actor_3_name'].replace(np.nan, 'unknown')
    df['movie_title'] = df['movie_title'].str.lower()
    df['metadata'] = df['actor_1_name'] + ' ' + df['actor_2_name'] + ' '+ df['actor_3_name'] + ' '+ df['director_name'] +' ' + df['genres']
    # print(df)
    # print(df.isna().sum())
    return df


def get_movies_from_wiki(links_dict, year):
    """
    year: Year of the movies
    return: Final DF with data extracted from TMDB
    """
    final_df = pd.DataFrame()
    # We have created loop so we can process more than one links given for a particular year
    print(links_dict)
    for link, wiki_table_indexes in links_dict.items():    
        df = process_wiki_movies(link, wiki_table_indexes, year)
        final_df = final_df.append(df)
    return final_df


if __name__ == "__main__":
    df_till_2016 = process_till_2016()
    df_till_2017 = process_for_2017(df_till_2016)
    # link1: Indian movies
    # link2: American movies link
    # wiki_table_indexes: Indexes of the tables in wikipedia which we needs to be scraped
    links_dict_2018 = {"https://en.wikipedia.org/wiki/List_of_American_films_of_2018": [2, 3, 4, 5], "https://en.wikipedia.org/wiki/List_of_Bollywood_films_of_2018": [2, 3, 4, 5]}
    df_2018 = get_movies_from_wiki(links_dict_2018, 2018)

    links_dict_2019 = {"https://en.wikipedia.org/wiki/List_of_American_films_of_2019": [3, 4, 5, 6], "https://en.wikipedia.org/wiki/List_of_Bollywood_films_of_2019": [3, 4, 5, 6]}
    df_2019 = get_movies_from_wiki(links_dict_2019, 2019)

    links_dict_2020 = {"https://en.wikipedia.org/wiki/List_of_American_films_of_2020": [3, 4, 5, 6], "https://en.wikipedia.org/wiki/List_of_Bollywood_films_of_2020": [3, 4, 5, 6]}
    df_2020 = get_movies_from_wiki(links_dict_2020, 2020)
    
    # # print(df_2020.isna().sum())
    final_df =  df_till_2017.append(df_2018.append(df_2019.append(df_2020,ignore_index=True),ignore_index=True),ignore_index=True)
    final_df = final_df.dropna(how='any')
    print(final_df)
    print(final_df.columns)
    final_df.to_csv('pre_process/output/content_filter_dataV1.csv',index=False)
