import bs4
import requests
import json

if __name__ == "__main__":
    pageHTMLCartelera = requests.get("http://www.cinemalaplata.com/cartelera.aspx").text
    soup = bs4.BeautifulSoup(pageHTMLCartelera, "html.parser")
    movies = soup.find_all('div', attrs={"class":"page-container singlepost"})
    movieList = []
    for movie in movies:
        link = movie.find('a').get('href')
        fullLink = "http://www.cinemalaplata.com/"+link
        movieHTLM = requests.get(fullLink).text
        movieSoup = bs4.BeautifulSoup(movieHTLM, "html.parser")
        movieData = movieSoup.find_all('div', attrs={"class":"dropcap6"})
        movieDict = {}

        #obtiene y parsea titulo de la película
        movieDict["Titulo"] = movieSoup.find_all('div', attrs={"class":"post-container page-title"})[0].string.strip()
        
        #parsea datos de la película
        for data in movieData:
            title = data.h4.string.strip()
            info = data.p.span.string
            if (title == "Actores") or (title == "Director"):
                #divide por ", "
                infoList = info.split(", ")
                #en muchos casos el último elemento viene con punto o espacios
                infoList[-1] = infoList[-1].replace('.','').strip()
                movieDict[title] = infoList
            elif (title == "Duracion"):
                #transforma el primero en numero
                movieDict[title] = int(info.split(" ")[0])
            else:
                movieDict[title]=info
        
        #parsea cines con sus funciones y horarios
        movieDict["Cines"] = []
        cinesData = movieSoup.find_all('div', attrs={'id':"ctl00_cph_pnFunciones"})[0].find_all('div')
        for cine in cinesData:
            cineDict = {}
            cineDict["Nombre"] = cine.h5.text.strip()
            funcionesData = cine.p.find_all('span')
            cineDict["Funciones"] = []
            for funciones in funcionesData:
                horaList = funciones.text.split(" ")
                #elimina elementos innecesarios '' y '-' de la lista
                horaList = list(filter(lambda x: (x != '' and x != '-'), horaList))
                funcionDict = {}
                #en la lista generada el primer elemento es el idioma y los demás horarios
                idioma = horaList.pop(0).replace(':','')
                funcionDict[idioma] = horaList
                cineDict["Funciones"].append(funcionDict)
            movieDict["Cines"].append(cineDict)

        movieList.append(movieDict)
    
    #guarda los datos en un json
    with open("cinemalaplata.json","w") as file:
        json.dump(movieList, file, ensure_ascii=False, indent=4)
