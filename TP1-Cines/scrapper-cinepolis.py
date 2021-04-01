import json
import time
from selenium import webdriver

if __name__ == "__main__":
    url = 'https://www.cinepolis.com.ar/'
    driver = webdriver.Chrome()
    driver.get(url)
    movies = driver.find_elements_by_css_selector('.movie-thumb.d-flex.flex-column.lg')
    links = []
    movieList = []
    for movie in movies:
        links.append(movie.get_attribute('href'))
    for link in links:
        driver.get(link)
        #tengo que clickear para que aparezca la info
        driver.find_element_by_xpath("//*[@id='tecnicos-tab']").click()
        movieData = driver.find_element_by_xpath("//*[@id='tecnicos']/p")
        while movieData.text == '':
            time.sleep(1)
        dataList = movieData.text.splitlines()
        dataDict = {}
        for data in dataList:
            atributos = data.split(": ")
            dataDict[atributos[0]] = atributos[1]
        movieList.append(dataDict)
    
    #guarda los datos en un json
    with open("cinepolis.json","w", encoding="utf-8") as file:
        json.dump(movieList, file, ensure_ascii=False, indent=4)