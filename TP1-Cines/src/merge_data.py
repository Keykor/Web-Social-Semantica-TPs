import json
import os
import unicodedata

def add_without_duplicates(list1, list2):
    new_list = []
    new_list.extend(list1)
    new_list.extend(list2)
    return list(set(new_list))

def normalizar_strings(s):
    s = unicodedata.normalize("NFD",s)
    return s.encode("utf8").decode("ascii","ignore").upper()

def title_equals(cinemalaplata, cinepolis, original):
    cinemalaplata = normalizar_strings(cinemalaplata)
    cinepolis = normalizar_strings(cinepolis)
    original = normalizar_strings(original)
    return cinemalaplata == cinepolis or cinemalaplata == original

def create_data_directory_path(file_name):
    return os.path.abspath(os.path.join(*[os.path.dirname(__file__), os.pardir, "data", file_name]))

def main():
    cinemalaplata_data = None
    cinepolis_data = None

    with open(create_data_directory_path('cinemalaplata.json'), encoding="utf-8") as file:
        cinemalaplata_data = json.load(file)
    with open(create_data_directory_path('cinepolis.json'), encoding="utf-8") as file:
        cinepolis_data = json.load(file)

    print("Merge de la información -> Comenzando")

    analized_movies = []
    for movie_cinepolis in cinepolis_data:
        movie_cinemalaplata = None
        for m in cinemalaplata_data:
            if title_equals(m['Titulo'], movie_cinepolis['Titulo'], movie_cinepolis['Título Original']):
                movie_cinemalaplata = m
                analized_movies.append(m)
                break
        
        if movie_cinemalaplata:
            movie_cinepolis["Web Oficial"] = movie_cinemalaplata["Web Oficial"]
            movie_cinepolis["Cines"].extend(movie_cinemalaplata["Cines"])
            movie_cinepolis["Actores"] = add_without_duplicates(movie_cinepolis["Actores"], movie_cinemalaplata["Actores"])
            movie_cinepolis["Director"] = add_without_duplicates(movie_cinepolis["Director"], movie_cinemalaplata["Director"])
            movie_cinepolis["Género"] = add_without_duplicates(movie_cinepolis["Género"], movie_cinemalaplata["Género"])
        else:
            movie_cinepolis["Web Oficial"] = "Desconocido"
        movie_cinepolis

    for movie in cinemalaplata_data:
        if movie not in analized_movies:
            movie["Título Original"] = "Desconocido"
            movie["Distribuidora"] = "Desconocido"
            cinepolis_data.append(movie)

    print("Merge de la información -> Terminado")

    with open(create_data_directory_path("merge.json"),"w",encoding="utf-8") as file:
        json.dump(cinepolis_data, file, ensure_ascii=False, indent=4)
    print("Merge de la información -> Guardado")

if __name__ == "__main__":
    main()