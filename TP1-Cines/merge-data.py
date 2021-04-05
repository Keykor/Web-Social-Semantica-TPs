import json

def add_without_duplicates(list1, list2):
    return list(set(list1.extend(list2)))

def title_equals(cinepolis, cinemalaplata, original):
    return cinemalaplata.upper() == cinepolis or cinemalaplata == original

if __name__ == "__main__":
    cinemalaplata_data = None
    cinepolis_data = None

    with open('cinemalaplata.json', encoding="utf-8") as file:
        cinemalaplata_data = json.load(file)
    with open('cinepolis.json', encoding="utf-8") as file:
        cinepolis_data = json.load(file)

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

    with open("merge.json","w",encoding="utf-8") as file:
        json.dump(cinepolis_data, file, ensure_ascii=False, indent=4)