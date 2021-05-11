import requests
import bs4
import json
import os
import json
from rdflib import Namespace, Graph, BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF

SCHEMA = Namespace("https://schema.org/")
MY_ONTOLOGY = Namespace("https://raw.githubusercontent.com/Keykor/Web-Social-Semantica-TPs/main/TP3-RDFyOWL/cohort.ttl#")
GRAPH = Graph()
GRAPH.namespace_manager.bind('', MY_ONTOLOGY)
COUNTER = {}
MOVIE_NAME = ""

def transform_to_triplets(objeto):
    if type(objeto) is not dict:
        return Literal(objeto)

    objeto.pop('@context', None)
    objeto.pop('@id', None)
    tipo = objeto.pop('@type', None)

    string_name = MOVIE_NAME + '_' + tipo + '_'
    if tipo == 'Review': 
        string_name += objeto['author']['name']
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
        relation = SCHEMA[clave]
        if type(valor) is list:
            for each in valor:
                GRAPH.add((nodo, relation, transform_to_triplets(each)))
        else:
            GRAPH.add((nodo, relation, transform_to_triplets(valor)))

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
        transform_to_triplets(data)
    
    with open(create_data_directory_path("individuals" + ".ttl"),"w",encoding="utf-8") as file:
        file.write(GRAPH.serialize(format="turtle").decode("utf-8"))

if __name__ == "__main__":
    main()