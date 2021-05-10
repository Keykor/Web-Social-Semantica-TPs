import json
from rdflib import Namespace, Graph, BNode, Literal, URIRef
from rdflib.namespace import OWL, RDF

SCHEMA = Namespace("https://schema.org/")
MY_ONTOLOGY = Namespace("https://raw.githubusercontent.com/Keykor/Web-Social-Semantica-TPs/main/TP3-RDFyOWL/cohort.ttl#")
GRAPH = Graph()
GRAPH.namespace_manager.bind('', MY_ONTOLOGY)

def transform_to_triplets(objeto):
    node = None
    if type(objeto) is dict:
        objeto.pop('@context', None)

        if 'name' in objeto:
            node = MY_ONTOLOGY[objeto['name'].replace(" ", "_")]
            GRAPH.add((node, RDF.type, OWL.NamedIndividual))
        else:
            node = BNode()

        tipo = objeto.pop('@type', None)
        GRAPH.add((node, RDF.type, SCHEMA[tipo]))

        for clave, valor in objeto.items():
            relation = SCHEMA[clave]
            if type(valor) is list:
                for each in valor:
                    GRAPH.add((node, relation, transform_to_triplets(each)))
            else:
                GRAPH.add((node, relation, transform_to_triplets(valor)))
    else:
        node = Literal(objeto)
    return node

def main():

    json_to_parse = None
    with open('imdb.json', encoding="utf-8") as file:
        json_to_parse = json.load(file)

    transform_to_triplets(json_to_parse)

    print(GRAPH.serialize(format="turtle").decode("utf-8"))

if __name__ == "__main__":
    main()