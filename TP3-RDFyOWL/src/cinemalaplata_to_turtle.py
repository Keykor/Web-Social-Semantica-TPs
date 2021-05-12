import json
import os
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
    with open(create_data_directory_path('cinemalaplata.json'), encoding="utf-8") as file:
        cinemalaplata_data = json.load(file)

    for movie in cinemalaplata_data:
        MOVIE_NAME = movie["Titulo"]
        string_name = 'Movie' + '_' + MOVIE_NAME
        MOVIE_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
        GRAPH.add((MOVIE_URI, RDF.type, OWL.NamedIndividual))
        GRAPH.add((MOVIE_URI, RDF.type, SCHEMA['Movie']))

        GRAPH.add((MOVIE_URI, SCHEMA['name'], Literal(movie["Titulo"])))
        GRAPH.add((MOVIE_URI, SCHEMA['description'], Literal(movie["Sinopsis"])))
        GRAPH.add((MOVIE_URI, SCHEMA['inLanguage'], Literal(movie["Idioma"])))
        GRAPH.add((MOVIE_URI, SCHEMA['url'], Literal(movie["Web Oficial"])))
        GRAPH.add((MOVIE_URI, SCHEMA['duration'], Literal(movie["Duracion"])))
        GRAPH.add((MOVIE_URI, SCHEMA['contentRating'], Literal(movie["Calificacion"])))

        create_individual_and_connect("Country", movie["Origen"], 'locationCreated', MOVIE_URI)
        for actor in movie["Actores"]:
            create_individual_and_connect("Person", actor, 'actor', MOVIE_URI)
        for director in movie["Director"]:
            create_individual_and_connect("Person", director, 'director', MOVIE_URI)

        for cine in movie["Cines"]:
            CINE_NAME = cine["Nombre"]
            string_name = 'MovieTheater' + '_' + CINE_NAME
            CINE_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
            GRAPH.add((CINE_URI, RDF.type, OWL.NamedIndividual))
            GRAPH.add((CINE_URI, RDF.type, SCHEMA['MovieTheater']))
            GRAPH.add((CINE_URI, SCHEMA['name'], Literal(CINE_NAME)))

            for funcion in cine["Funciones"]:
                SALA = funcion["Sala"]
                string_name = 'ScreeningEvent' + '_' + CINE_NAME + '_' + SALA + '_' + MOVIE_NAME
                event_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
                GRAPH.add((event_URI, RDF.type, OWL.NamedIndividual))
                GRAPH.add((event_URI, RDF.type, SCHEMA['ScreeningEvent']))
                GRAPH.add((event_URI, SCHEMA['workPresented'], MOVIE_URI))
                GRAPH.add((event_URI, SCHEMA['inLanguage'], Literal(funcion["Idioma"]))) 
                for time in funcion["Hora"]:
                    GRAPH.add((event_URI, SCHEMA['startTime'], Literal(time)))
                GRAPH.add((CINE_URI, SCHEMA['event'], event_URI))

    with open(create_data_directory_path("individualsCinemalaplata" + ".ttl"),"w",encoding="utf-8") as file:
        file.write(GRAPH.serialize(format="turtle").decode("utf-8"))


if __name__ == "__main__":
    main()