import json
import os

def create_data_directory_path(file_name):
    return os.path.abspath(os.path.join(*[os.path.dirname(__file__), os.pardir, "data", file_name]))

def dict_prop_comparison(item1, item2):
    if item1['@type'] == 'Person' and item2['@type'] == 'Person':
        return item1['name'] == item2['name']
    elif item1['@type'] == 'Organization' and item2['@type'] == 'Organization':
        return item1['url'] == item2['url']
    return False

def string_prop_comparison(item1, item2):
    return item1 == item2

def review_prop_comparison(item1, item2):
    return item1['author']['name'] == item2['author']['name']

def main():
    pages_to_scrap = None
    with open(create_data_directory_path('pages_to_scrap.json'), encoding="utf-8") as file:
        pages_to_scrap = json.load(file)

    #movie['aggregateRating'] = [] (en duda como guardarlo)
    #Revisando los datos que brinda cada página elegí cuales quiero quedarme
    #y de qué forma, si simples o lista
    properties_list_simple = ['@context', '@type', 'name', 'image', 'description', 'duration', 'trailer', 'productionCompany', 'countryOfOrigin', 'releasedEvent', 'hasPart']
    properties_list_list = ['aggregateRating', 'genre', 'actor', 'director', 'creator', 'review', 'author', 'character']

    movie = {}
    for prop in properties_list_simple:
        movie[prop] = None
    for prop in properties_list_list:
        movie[prop] = []

    for page in pages_to_scrap:
        with open(create_data_directory_path(page["name"] + '.json'), encoding="utf-8") as file:
            page_movie = json.load(file)
        
        for prop in properties_list_simple:
            if prop in page_movie and not movie[prop]:
                movie[prop] = page_movie[prop]
        
        for prop in properties_list_list:
            if prop in page_movie:
                if prop == 'genre' or prop == 'character':
                    comparison_method = string_prop_comparison
                elif prop == 'review':
                    comparison_method = review_prop_comparison
                else:
                    comparison_method = dict_prop_comparison

                #A veces el dato que quiero que sea una lista en la extraccion no es una lista
                if not isinstance(page_movie[prop], list):
                    page_movie[prop] = [page_movie[prop]]

                for item_page_movie in page_movie[prop]:
                    founded = False
                    for item_movie in movie[prop]:
                        if comparison_method(item_movie, item_page_movie):
                            founded = True
                            break
                    if not founded:
                        movie[prop].append(item_page_movie)
    
    with open(create_data_directory_path("merge.json"),"w",encoding="utf-8") as file:
        json.dump(movie, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()