import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of, element_to_be_clickable
from selenium.webdriver.common.by import By

def main():
    print("Scrapping de Cinepolis -> Comenzando")
    url = 'https://www.cinepolis.com.ar/'
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    movies = driver.find_elements_by_css_selector('.movie-thumb.d-flex.flex-column.lg')
    links = []
    movie_list = []

    #guarda los links de las películas en una lista
    for movie in movies:
        links.append(movie.get_attribute('href'))

    for link in links:
        driver.get(link)

        #parsea título y sinopsis de la película
        movie_dict = {}
        movie_dict["Titulo"] = driver.find_element_by_xpath("//*[@id='app']/main/div[1]/div/h2").text
        movie_dict["Sinopsis"] = driver.find_element_by_xpath("//*[@id='sinopsis']").text

        #clickea y espera para que aparezca la info técnica
        movie_info = driver.find_element_by_xpath("//*[@id='tecnicos']")
        driver.find_element_by_xpath("//*[@id='tecnicos-tab']").click()
        WebDriverWait(driver, timeout=5).until(lambda x: 'show' in movie_info.get_attribute('class'))

        #parsea los datos técnicos
        movie_info_list = movie_info.text.splitlines()
        for info in movie_info_list:
            data = info.split(": ")
            if data[0] == "Actores" or data[0] == "Director" or data[0] == "Género":
                #divide el string por ", "
                movie_dict[data[0]] = data[1].split(", ")
            elif data[0] == "Duración":
                #transforma la duracion de string a en numero
                movie_dict[data[0]] = int(data[1].split(" ")[0])
            else:
                movie_dict[data[0]] = data[1]

        #espera a que esté el panel
        WebDriverWait(driver, timeout=5).until(element_to_be_clickable((By.XPATH, "//*[@id='app']/main/div[2]/div/div[2]/div/div/div[2]")))
        cines_list = driver.find_elements_by_xpath("//*[@class='card panel panel-primary']")

        #parsea los cines y las funciones
        movie_dict['Cines'] = []
        for cine in cines_list:
            #clickea y espera que el panel se expanda totalmente
            panel_element = cine.find_element_by_class_name('panel-collapse.collapse')
            cine.click()
            WebDriverWait(driver, 5).until(lambda x: 'show' in panel_element.get_attribute('class'))

            data_list = cine.text.splitlines() 
            cine_dict = {}
            cine_dict['Nombre'] = data_list.pop(0)
            
            #pueden aparecer datos con la misma sala y formato pero separados
            #entonces primero los proceso y luego los guardo
            appeared_types = {}
            actual_type = ''
            for data in data_list:
                try:
                    time.strptime(data,'%H:%M')
                    appeared_types[actual_type].append(data)
                except:
                    actual_type = data
                    if actual_type not in appeared_types:
                        appeared_types[data] = []

            cine_dict['Funciones'] = []
            for key in appeared_types:
                typesList = key.split(' • ')
                show = {}
                show['Sala'] = typesList[0] 
                show['Formato'] = typesList[1]
                show['Idioma'] = typesList[2]
                show['Horas'] = appeared_types[key]
                cine_dict['Funciones'].append(show)

            movie_dict['Cines'].append(cine_dict)

        movie_list.append(movie_dict)
    driver.quit()
    print("Scrapping de Cinepolis -> Terminado")

    #guarda los datos en un json
    data_directory = os.path.join(*[os.path.dirname(__file__), os.pardir, "data", "cinepolis.json"])
    with open(os.path.abspath(data_directory),"w", encoding="utf-8") as file:
        json.dump(movie_list, file, ensure_ascii=False, indent=4)
    print("Scrapping de Cinepolis -> Guardado")

if __name__ == "__main__":
    main()