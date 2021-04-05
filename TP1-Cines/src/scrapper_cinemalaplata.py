import bs4
import requests
import json
import os

def main():
    print("Scrapping de Cinema La Plata -> Comenzando")
    pageHTMLCartelera = requests.get("http://www.cinemalaplata.com/cartelera.aspx").text
    soup = bs4.BeautifulSoup(pageHTMLCartelera, "html.parser")
    movies = soup.find_all('div', attrs={"class":"page-container singlepost"})
    movieList = []
    for movie in movies:
        link = movie.find('a').get('href')
        fullLink = "http://www.cinemalaplata.com/"+link
        movie_HTLM = requests.get(fullLink).text
        movie_Soup = bs4.BeautifulSoup(movie_HTLM, "html.parser")
        movie_data = movie_Soup.find_all('div', attrs={"class":"dropcap6"})
        movie_dict = {}

        #obtiene y parsea titulo y sinopsis de la película
        movie_dict["Titulo"] = movie_Soup.find_all('div', attrs={"class":"post-container page-title"})[0].string.strip()
        movie_dict["Sinopsis"] = movie_Soup.find_all('span', attrs={"id":"ctl00_cph_lblSinopsis"})[0].string.strip()

        #parsea datos de la película
        for data in movie_data:
            title = data.h4.string.strip()
            info = data.p.span.string
            if (title == "Actores") or (title == "Director"):
                #divide por ", "
                info_list = info.split(", ")
                #en muchos casos el último elemento viene con punto o espacios
                info_list[-1] = info_list[-1].replace('.','').strip()
                movie_dict[title] = info_list
            elif (title == "Duracion"):
                #transforma el primero en numero
                movie_dict[title] = int(info.split(" ")[0])
            elif (title == "Género"):
                if (", " in info):
                    movie_dict[title] = info.split(", ")
                elif (" / " in info):
                    movie_dict[title] = info.split(" / ")
                else:
                    movie_dict[title] = [info]            
            else:
                movie_dict[title]=info
        
        #parsea cines con sus funciones y horarios
        cines_data = movie_Soup.find_all('div', attrs={'id':"ctl00_cph_pnFunciones"})
        cines_data = cines_data[0].find_all('div')

        movie_dict["Cines"] = []
        for cine in cines_data:
            cine_data_list = cine.h5.text.strip().split(" - ")
            theater_type = cine_data_list[1].split()[-1]
            shows_data = cine.p.find_all('span')

            cine_dict = {}
            cine_dict["Nombre"] = cine_data_list[0]

            cine_dict["Funciones"] = []
            for show in shows_data:
                hours_list = show.text.split(" ")

                #elimina elementos innecesarios '' y '-' de la lista
                hours_list = list(filter(lambda x: (x != '' and x != '-'), hours_list))

                #en la lista generada el primer elemento es el idioma y los demás horarios
                language = hours_list.pop(0).replace(':','')

                show_dict = {}
                show_dict["Sala"] = theater_type
                show_dict["Idioma"] = language
                show_dict["Hora"] = hours_list
                cine_dict["Funciones"].append(show_dict)
                
            movie_dict["Cines"].append(cine_dict)

        movieList.append(movie_dict)
    print("Scrapping de Cinema La Plata -> Terminado")

    #guarda los datos en un json
    
    data_directory = os.path.join(*[os.path.dirname(__file__), os.pardir, "data", "cinemalaplata.json"])
    with open(os.path.abspath(data_directory),"w",encoding="utf-8") as file:
        json.dump(movieList, file, ensure_ascii=False, indent=4)
    print("Scrapping de Cinema La Plata -> Guardado")

if __name__ == "__main__":
    main()