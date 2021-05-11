import json
from rdflib import Namespace, Graph, BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF

SCHEMA = Namespace("https://schema.org/")
MY_ONTOLOGY = Namespace("https://raw.githubusercontent.com/Keykor/Web-Social-Semantica-TPs/main/TP3-RDFyOWL/cohort.ttl#")
GRAPH = Graph()
GRAPH.namespace_manager.bind('', MY_ONTOLOGY)

def transform_to_triplets(URI_relativa_padre, objeto):
    if type(objeto) is not dict:
        return Literal(objeto)

    objeto.pop('@context', None)
    tipo = objeto.pop('@type', None)

    if tipo == "Rating":
        string_name = tipo + "_" + URI_relativa_padre
    elif tipo == "Review" or tipo == "AggregateRating":
        string_name = tipo + "_" + objeto['author']['name'] + "_" + URI_relativa_padre
    elif 'name' in objeto:
        string_name = objeto['name']
    elif 'url' in objeto:
        string_name = tipo + "_" + objeto['url']
    elif 'embedUrl' in objeto:
        string_name = tipo + "_" + objeto['embedUrl']
    elif 'contentUrl' in objeto:
        string_name = tipo + "_" + objeto['contentUrl']
    
    URI_relativa = string_name.replace(" ", "_")
    nodo = MY_ONTOLOGY[URI_relativa]
    GRAPH.add((nodo, RDF.type, OWL.NamedIndividual))
    GRAPH.add((nodo, RDF.type, SCHEMA[tipo]))

    for clave, valor in objeto.items():
        relation = SCHEMA[clave]
        if type(valor) is list:
            for each in valor:
                GRAPH.add((nodo, relation, transform_to_triplets(URI_relativa, each)))
        else:
            GRAPH.add((nodo, relation, transform_to_triplets(URI_relativa, valor)))

    return nodo

def main():

    json_to_parse = None
    with open('imdb.json', encoding="utf-8") as file:
        json_to_parse = json.load(file)

    transform_to_triplets("", json_to_parse)

    with open("imdb.ttl","w",encoding="utf-8") as file:
        file.write(GRAPH.serialize(format="turtle").decode("utf-8"))

if __name__ == "__main__":
    main()