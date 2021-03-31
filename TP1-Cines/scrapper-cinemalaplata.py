import bs4
import requests

if __name__ == "__main__":
    pageHTMLCartelera = requests.get("http://www.cinemalaplata.com/cartelera.aspx").text
    soup = bs4.BeautifulSoup(pageHTMLCartelera, "html.parser")
    movies = soup.find_all('div', attrs={"class":"page-container singlepost"})
    for movie in movies:
        link = movie.find('a').get('href')
        fullLink = "http://www.cinemalaplata.com/"+link
        movieHTLM = requests.get(fullLink).text
        movieSoup = bs4.BeautifulSoup(movieHTLM, "html.parser")
        movieData = movieSoup.find_all('div', attrs={"class":"dropcap6"})
        movieDict = {}

        #parsea titulo
        movieDict["Titulo"] = movieSoup.find_all('div', attrs={"class":"post-container page-title"})[0].string.strip()
        
        #parsea datos
        for data in movieData:
            title = data.h4.string.strip()
            info = data.p.span.string
            movieDict[title]=info
        
        #parsea horarios
        movieDict["Cines"] = []
        cinesData = movieSoup.find_all('div', attrs={'id':"ctl00_cph_pnFunciones"})[0].find_all('div')
        for cine in cinesData:
            cineDict = {}
            cineDict["Nombre"] = cine.h5.text.strip()
            horasData = cine.p.find_all('span')
            for hora in horasData:
                horaList = hora.text.split(" ")
                horaList = list(filter(lambda x: (x != '' and x != '-'), horaList))
                cineDict[horaList.pop(0)] = horaList
                
            movieDict["Cines"].append(cineDict)

        print(movieDict)