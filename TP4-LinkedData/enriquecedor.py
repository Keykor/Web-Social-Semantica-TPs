import requests
import rdflib
import sys
from rdflib.namespace import Namespace, OWL

DBO = Namespace("http://dbpedia.org/ontology/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

def main():
    if len(sys.argv) < 3:
        print("Faltan argumentos")
        return

    g = rdflib.Graph()

    #agrega al grafo los links
    g.parse(sys.argv[2], format="turtle", encoding="utf-8")

    #me guardo los links de dbpedia de las tripletas
    links = []
    for s, p, o in g.triples((None, OWL.sameAs, None)):
        links.append(o)

    #recorro los links para obtener el ttl de cada actor y agregar su info al grafo
    for link in links:
        r = requests.get(link, headers={'Accept': 'text/turtle'})
        graph_actor = rdflib.Graph()
        graph_actor.parse(data=r.text, format="turtle", encoding="utf-8")

        #para agregar la página de Wikipedia
        for triplet in graph_actor.triples((None, FOAF['isPrimaryTopicOf'], None)):
            g.add(triplet)

        #para agregar la fecha de nacimiento
        for triplet in graph_actor.triples((None, DBO['birthDate'], None)):
            g.add(triplet)

        #para agregar las ocupaciones
        for s, p, o in graph_actor.triples((None, DBO['occupation'], None)):
            g.add((s, p, o))

            #ocuppation tiene una uri donde los title son las diferentes ocupaciones de la persona
            req = requests.get(o, headers={'Accept': 'text/turtle'})
            graph_occupation = rdflib.Graph()
            graph_occupation.parse(data=req.text, format="turtle", encoding="utf-8")
            for triplet in graph_occupation.triples((None, DBO['title'], None)):
                g.add(triplet)

    #agrega al grafo el dataset del primer argumento
    g.parse(sys.argv[1], format="turtle", encoding="utf-8")

    print(g.serialize(format="turtle").decode("utf-8"))

if __name__ == "__main__":
    main()