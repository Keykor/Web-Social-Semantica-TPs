import json
import os

def create_data_directory_path(file_name):
    return os.path.abspath(os.path.join(*[os.path.dirname(__file__), os.pardir, "data", file_name]))

# Como IMDB da url relativos a su página, los completo 
# para que al mergear se sepa de dónde vienen
def change_imdb_url(dictionary):
    for key in dictionary:
        if isinstance(dictionary[key], dict):
            change_imdb_url(dictionary[key])
        elif isinstance(dictionary[key], list):
            for elem in dictionary[key]:
                if isinstance(elem, dict):
                    change_imdb_url(elem)
        elif key == 'url':
            if 'https://www.imdb.com' not in dictionary[key]:
                dictionary[key] = 'https://www.imdb.com' + dictionary[key]

# En el scrappeo de Rotten Tomatoes hay una clave llamada
# 'actors' que debería llamarse 'actor' para respetar el esquema
def change_actor_prop_name(movie):
    if 'actors' in movie:
        movie['actor'] = movie.pop('actors')

# En el scrappeo de Rotten Tomatoes pueden haber varios géneros
# diferentes en un solo string separados por ' & '
def separate_genres(movie):
    newList = []
    for genre in movie['genre']:
        if ' & ' in genre:
            newList.extend(genre.split(' & '))
        else:
            newList.append(genre)
    movie['genre'] = newList

# Agrega organización de dónde proviene al valor 'aggregateRating'
# para que al mergear la info no se pierda
def add_organization_to_aggregate_rating(movie, name, url):
    movie['aggregateRating']['author'] = {"@type": "Organization", "name": name, "url": url}

def main():
    pages_to_scrap = None
    with open(create_data_directory_path('pages_to_scrap.json'), encoding="utf-8") as file:
        pages_to_scrap = json.load(file)
    
    for page in pages_to_scrap:
        with open(create_data_directory_path(page["name"] + '.json'), encoding="utf-8") as file:
            movie = json.load(file)
        
        if page['name'] == 'imdb':
            change_imdb_url(movie)
        elif page['name'] == 'rottentomatoes':
            change_actor_prop_name(movie)
            separate_genres(movie)

        add_organization_to_aggregate_rating(movie, page['realName'], page['website'])

        with open(create_data_directory_path(page["name"] + ".json"),"w",encoding="utf-8") as file:
            json.dump(movie, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()