import rdflib
import requests
import bs4
import json
import os
import json
from rdflib import Namespace, Graph, Literal
from rdflib.namespace import OWL, RDF, XSD, RDFS
from datetime import datetime

SCHEMA = Namespace("https://schema.org/")
MY_ONTOLOGY = Namespace("https://raw.githubusercontent.com/Keykor/Web-Social-Semantica-TPs/main/TP3-RDFyOWL/cohort.ttl#")
GRAPH = Graph()
GRAPH.namespace_manager.bind('', MY_ONTOLOGY)
GRAPH.namespace_manager.bind('sch', SCHEMA)
COUNTER = {}
MOVIE_NAME = ""
ACTUAL_PAGE = ""

def datatype(tipo):
    if tipo in ['worstRating', 'ratingValue', 'bestRating']:
        return XSD.float
    elif tipo in ['videoFormat', 'timeRequired', 'reviewBody', 'name', 'keywords', 'inLanguage', 'genre', 'description', 'countryOfOrigin', 'contentUrl', 'contentRating', 'character', 'category', 'datePublished', 'uploadDate']:
        return XSD.string
    elif tipo in ['urlTemplate', 'url', 'thumbnailUrl', 'sameAs', 'mainEntityOfPage', 'image', 'embedUrl', 'actionPlatform']:
        return XSD.anyURL
    elif tipo in ['startTime', 'startDate', 'dateModified', 'dateCreated', 'availabilityStarts']:
        return XSD.dateTime
    elif tipo in ['reviewCount', 'ratingCount', 'duration']:
        return XSD.integer
    else:
        return RDFS.Literal

def make_literal(value, tipo):
    value_type = datatype(tipo)
    if (tipo == 'duration') and ("PT" in value):
        newValue = value.replace("PT", "")
        newValue = newValue.replace("M", "")
        if "H" in newValue:
            newValue = newValue.split("H")
            value = 60 * int(newValue[0]) + int(newValue[1])
        else:
            value = int(newValue)
    elif (value_type == XSD.dateTime) and not ("T" in value):
        if (" " in value):
            value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            value = datetime.strptime(value, '%Y-%m-%d')
    elif (tipo == 'ratingValue') and (type(value) is str):
        value = value.replace(",",".")
    return Literal(value, datatype=value_type)

def transform_to_triplets(objeto):
    objeto.pop('@context', None)
    objeto.pop('@id', None)
    tipo = objeto.pop('@type', None)

    string_name = MOVIE_NAME + '_' + tipo + '_'
    if tipo == 'Review': 
        string_name += objeto['author']['name']
    elif tipo == 'AggregateRating':
        string_name += ACTUAL_PAGE
    elif 'name' in objeto:
        if tipo in ["Person", "Organization", "Country"]:
            string_name = tipo + '_' + objeto['name'] 
        else:
            string_name += objeto['name'] 
    else:
        if tipo not in COUNTER:
            COUNTER[tipo] = 0
        string_name += str(COUNTER[tipo])
        COUNTER[tipo] = COUNTER[tipo] + 1 

    nodo = MY_ONTOLOGY[string_name.replace(" ", "_")]
    GRAPH.add((nodo, RDF.type, OWL.NamedIndividual))
    GRAPH.add((nodo, RDF.type, SCHEMA[tipo]))

    for clave, valor in objeto.items():
        if valor:
            if type(valor) is list:
                for each in valor:
                    if type(each) is dict:
                        GRAPH.add((nodo, SCHEMA[clave], transform_to_triplets(each)))
                    else:
                        GRAPH.add((nodo, MY_ONTOLOGY[clave], make_literal(each, clave)))
            else:
                if type(valor) is dict:
                    GRAPH.add((nodo, SCHEMA[clave], transform_to_triplets(valor)))
                else:
                    GRAPH.add((nodo, MY_ONTOLOGY[clave], make_literal(valor,clave)))

    return nodo

def create_data_directory_path(file_name):
    return os.path.abspath(os.path.join(*[os.path.dirname(__file__), os.pardir, "data", file_name]))

def main():
    pages_to_scrap = None
    with open(create_data_directory_path('pages_to_scrap.json'), encoding="utf-8") as file:
        pages_to_scrap = json.load(file)

    for page in pages_to_scrap:
        #Utilizo un user agent para scrapear que represente una PC de escritorio con Windows 10 usando algún navegador
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        pageHTML = requests.get(page["url"], headers=headers).text
        soup = bs4.BeautifulSoup(pageHTML, "html.parser")
        data_json = soup.find('script', attrs={"type":"application/ld+json"}).string.replace("\r","").replace("\n","").replace("\t","")
        data = json.loads(data_json)

        global MOVIE_NAME
        MOVIE_NAME = data['name']
        global ACTUAL_PAGE
        ACTUAL_PAGE = page['name']
        transform_to_triplets(data)
    
    with open(create_data_directory_path("individuals" + ".ttl"),"w",encoding="utf-8") as file:
        file.write(GRAPH.serialize(format="turtle").decode("utf-8"))

if __name__ == "__main__":
    main()