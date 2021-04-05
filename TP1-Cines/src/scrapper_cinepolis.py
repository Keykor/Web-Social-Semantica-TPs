import json
import time
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of, element_to_be_clickable
from selenium.webdriver.common.by import By

def main():
    print("Scrapping de Cinepolis -> Comenzando")
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

        #parsea título y sinopsis de la película
        dataDict = {}
        dataDict["Titulo"] = driver.find_element_by_xpath("//*[@id='app']/main/div[1]/div/h2").text
        dataDict["Sinopsis"] = driver.find_element_by_xpath("//*[@id='sinopsis']").text

        #tengo que clickear para que aparezca la info técnica
        movieData = driver.find_element_by_xpath("//*[@id='tecnicos']")
        driver.find_element_by_xpath("//*[@id='tecnicos-tab']").click()
        WebDriverWait(driver, timeout=5).until(lambda x: 'show' in movieData.get_attribute('class'))

        #parsea los datos técnicos
        dataList = movieData.text.splitlines()
        for data in dataList:
            atributos = data.split(": ")
            if atributos[0] == "Actores" or atributos[0] == "Director" or atributos[0] == "Género":
                #divide por ", "
                atributos[1]
                infoList = atributos[1].split(", ")
                dataDict[atributos[0]] = infoList
            elif (atributos[0] == "Duración"):
                #transforma el primero en numero
                dataDict[atributos[0]] = int(atributos[1].split(" ")[0])
            else:
                dataDict[atributos[0]] = atributos[1]

        WebDriverWait(driver, timeout=5).until(element_to_be_clickable((By.XPATH, "//*[@id='app']/main/div[2]/div/div[2]/div/div/div[2]")))
        cinesList = driver.find_elements_by_xpath("//*[@class='card panel panel-primary']")

        dataDict['Cines'] = []
        for cine in cinesList:
            panel_element = cine.find_element_by_class_name('panel-collapse.collapse')
            cine.click()
            WebDriverWait(driver, 5).until(lambda x: 'show' in panel_element.get_attribute('class'))

            dataList = cine.text.splitlines() 
            cineDict = {}
            cineDict['Nombre'] = dataList.pop(0)
            
            typesAparecidos = {}
            typesActual = ''
            for data in dataList:
                try:
                    time.strptime(data,'%H:%M')
                    typesAparecidos[typesActual].append(data)
                except:
                    typesActual = data
                    if typesActual not in typesAparecidos:
                        typesAparecidos[data] = []

            cineDict['Funciones'] = []
            for key in typesAparecidos:
                typesList = key.split(' • ')
                funcion = {}
                funcion['Sala'] = typesList[0] 
                funcion['Formato'] = typesList[1]
                funcion['Idioma'] = typesList[2]
                funcion['Horas'] = typesAparecidos[key]
                cineDict['Funciones'].append(funcion)

            dataDict['Cines'].append(cineDict)

        movieList.append(dataDict)
    driver.quit()
    print("Scrapping de Cinepolis -> Terminado")

    #guarda los datos en un json
    data_directory = os.path.join(*[os.path.dirname(__file__), os.pardir, "data", "cinepolis.json"])
    with open(os.path.abspath(data_directory),"w", encoding="utf-8") as file:
        json.dump(movieList, file, ensure_ascii=False, indent=4)
    print("Scrapping de Cinepolis -> Guardado")

if __name__ == "__main__":
    main()