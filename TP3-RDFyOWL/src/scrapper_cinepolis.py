import datetime
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import visibility_of, element_to_be_clickable
from selenium.webdriver.common.by import By
from rdflib import Namespace, Graph, BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF

SCHEMA = Namespace("https://schema.org/")
MY_ONTOLOGY = Namespace("https://raw.githubusercontent.com/Keykor/Web-Social-Semantica-TPs/main/TP3-RDFyOWL/cohort.ttl#")
GRAPH = Graph()
GRAPH.namespace_manager.bind('', MY_ONTOLOGY)

def create_data_directory_path(file_name):
    return os.path.abspath(os.path.join(*[os.path.dirname(__file__), os.pardir, "data", file_name]))

def create_individual_and_connect(tipo, data, relation, URI_to_connect):
    string_name = tipo + '_' + data
    each_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
    GRAPH.add((each_URI, RDF.type, OWL.NamedIndividual))
    GRAPH.add((each_URI, RDF.type, SCHEMA[tipo]))
    GRAPH.add((each_URI, SCHEMA['name'], Literal(data)))
    GRAPH.add((URI_to_connect, SCHEMA[relation], each_URI))
    return each_URI

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
    cines_list = []

    #guarda los links de las películas en una lista
    for movie in movies:
        links.append(movie.get_attribute('href'))

    for link in links:
        driver.get(link)

        #parsea título y sinopsis de la película

        MOVIE_NAME = driver.find_element_by_xpath("//*[@id='app']/main/div[1]/div/h2").text
        string_name = 'Movie' + '_' + MOVIE_NAME
        MOVIE_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
        GRAPH.add((MOVIE_URI, RDF.type, OWL.NamedIndividual))
        GRAPH.add((MOVIE_URI, RDF.type, SCHEMA['Movie']))

        name_literal = Literal(MOVIE_NAME)
        GRAPH.add((MOVIE_URI, SCHEMA['name'], name_literal))

        description_literal = Literal(driver.find_element_by_xpath("//*[@id='sinopsis']").text)
        GRAPH.add((MOVIE_URI, SCHEMA['description'], description_literal))
        

        #clickea y espera para que aparezca la info técnica
        movie_info = driver.find_element_by_xpath("//*[@id='tecnicos']")
        driver.find_element_by_xpath("//*[@id='tecnicos-tab']").click()
        WebDriverWait(driver, timeout=5).until(lambda x: 'show' in movie_info.get_attribute('class'))

        #parsea los datos técnicos
        movie_info_list = movie_info.text.splitlines()
        for info in movie_info_list:
            data = info.split(": ")
            if len(data) > 1:
                if data[0] == "Actores" or data[0] == "Director" or data[0] == "Origen":
                    #divide el string por ", "
                    data_list = data[1].split(", ")
                    relation = "actor"
                    tipo = "Person"
                    if data[0] == "Director":
                        relation = "director"
                    elif data[0] == "Origen":
                        relation = "locationCreated"
                        tipo = "Country"
                    for each in data_list:
                        create_individual_and_connect(tipo, each, relation, MOVIE_URI)
                elif data[0] == "Género":
                    data_list = data[1].split(", ")
                    for each in data_list:
                        GRAPH.add((MOVIE_URI, SCHEMA['genre'], Literal(each)))
                elif data[0] == "Duración":
                    #transforma la duracion de string a en numero
                    aux = int(data[1].split(" ")[0])
                    GRAPH.add((MOVIE_URI, SCHEMA['duration'], Literal(aux)))
                elif data[0] == "Distribuidora":
                    create_individual_and_connect('Organization', data[1], 'publisher', MOVIE_URI)
                elif data[0] == "Calificación":
                    GRAPH.add((MOVIE_URI, SCHEMA['contentRating'], Literal(data[1])))
                elif data[0] == "Título Original":
                    GRAPH.add((MOVIE_URI, SCHEMA['name'], Literal(data[1])))     

        #espera a que esté el panel
        WebDriverWait(driver, timeout=5).until(element_to_be_clickable((By.XPATH, "//*[@id='app']/main/div[2]/div/div[2]/div/div/div[2]")))
        cines_to_iterate = driver.find_elements_by_xpath("//*[@class='card panel panel-primary']")

        #parsea los cines y las funciones
        for cine in cines_to_iterate:
            #clickea y espera que el panel se expanda totalmente
            panel_element = cine.find_element_by_class_name('panel-collapse.collapse')
            cine.click()
            WebDriverWait(driver, 5).until(lambda x: 'show' in panel_element.get_attribute('class'))

            data_list = cine.text.splitlines() 
            CINE_NAME = data_list.pop(0)
            string_name = 'MovieTheater' + '_' + CINE_NAME
            CINE_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
            GRAPH.add((CINE_URI, RDF.type, OWL.NamedIndividual))
            GRAPH.add((CINE_URI, RDF.type, SCHEMA['MovieTheater']))
            GRAPH.add((CINE_URI, SCHEMA['name'], Literal(CINE_NAME)))
            
            #pueden aparecer datos con l6a misma sala y formato pero separados
            appeared_types = {}
            actual_type = ''
            for data in data_list:
                try:
                    datetime.datetime.strptime(data,'%H:%M')
                    appeared_types[actual_type].append(data)
                except:
                    actual_type = data
                    if actual_type not in appeared_types:
                        appeared_types[data] = []

            for key in appeared_types:
                typesList = key.split(' • ')
                SALA = typesList[0] + ' ' + typesList[1]
                string_name = 'ScreeningEvent' + '_' + CINE_NAME + '_' + SALA + '_' + MOVIE_NAME
                event_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
                GRAPH.add((event_URI, RDF.type, OWL.NamedIndividual))
                GRAPH.add((event_URI, RDF.type, SCHEMA['ScreeningEvent']))
                GRAPH.add((event_URI, SCHEMA['workPresented'], MOVIE_URI))
                GRAPH.add((event_URI, SCHEMA['videoFormat'], Literal(SALA)))
                GRAPH.add((event_URI, SCHEMA['inLanguage'], Literal(typesList[2])))
                for time in appeared_types[key]:
                    GRAPH.add((event_URI, SCHEMA['startTime'], Literal(time)))
                GRAPH.add((CINE_URI, SCHEMA['event'], event_URI))
            

    driver.quit()
    print("Scrapping de Cinepolis -> Terminado")

    with open(create_data_directory_path("individualsCinepolis" + ".ttl"),"w",encoding="utf-8") as file:
        file.write(GRAPH.serialize(format="turtle").decode("utf-8"))

    print("Scrapping de Cinepolis -> Guardado")

if __name__ == "__main__":
    main()