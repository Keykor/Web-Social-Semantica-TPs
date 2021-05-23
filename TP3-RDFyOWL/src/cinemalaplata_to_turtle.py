import json
import os
from rdflib import Namespace, Graph, Literal
from rdflib.namespace import OWL, RDF, XSD
from datetime import datetime

SCHEMA = Namespace("https://schema.org/")
MY_ONTOLOGY = Namespace("https://raw.githubusercontent.com/Keykor/Web-Social-Semantica-TPs/main/TP3-RDFyOWL/cohort.ttl#")
GRAPH = Graph()
GRAPH.namespace_manager.bind('', MY_ONTOLOGY)
GRAPH.namespace_manager.bind('sch', SCHEMA)

def create_data_directory_path(file_name):
    return os.path.abspath(os.path.join(*[os.path.dirname(__file__), os.pardir, "data", file_name]))

def create_individual_and_connect(tipo, data, relation, URI_to_connect):
    string_name = tipo + '_' + data
    each_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
    GRAPH.add((each_URI, RDF.type, OWL.NamedIndividual))
    GRAPH.add((each_URI, RDF.type, SCHEMA[tipo]))
    GRAPH.add((each_URI, MY_ONTOLOGY['name'], Literal(data, datatype=XSD.string)))
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

        GRAPH.add((MOVIE_URI, MY_ONTOLOGY['name'], Literal(movie["Titulo"], datatype=XSD.string)))
        GRAPH.add((MOVIE_URI, MY_ONTOLOGY['description'], Literal(movie["Sinopsis"], datatype=XSD.string)))
        GRAPH.add((MOVIE_URI, MY_ONTOLOGY['inLanguage'], Literal(movie["Idioma"], datatype=XSD.string)))
        if (movie["Web Oficial"] != 'No disponible'):
            GRAPH.add((MOVIE_URI, MY_ONTOLOGY['url'], Literal(movie["Web Oficial"], datatype=XSD.anyURI)))
        GRAPH.add((MOVIE_URI, MY_ONTOLOGY['duration'], Literal(movie["Duracion"], datatype=XSD.integer)))
        GRAPH.add((MOVIE_URI, MY_ONTOLOGY['contentRating'], Literal(movie["Calificacion"], datatype=XSD.string)))

        create_individual_and_connect("Country", movie["Origen"], 'locationCreated', MOVIE_URI)
        for actor in movie["Actores"]:
            create_individual_and_connect("Person", actor, 'actor', MOVIE_URI)
        for director in movie["Director"]:
            create_individual_and_connect("Person", director, 'director', MOVIE_URI)

        for genero in movie["Género"]:
            GRAPH.add((MOVIE_URI, MY_ONTOLOGY['genre'], Literal(genero, datatype=XSD.string)))

        for cine in movie["Cines"]:
            CINE_NAME = cine["Nombre"]
            string_name = 'MovieTheater' + '_' + CINE_NAME
            CINE_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
            GRAPH.add((CINE_URI, RDF.type, OWL.NamedIndividual))
            GRAPH.add((CINE_URI, RDF.type, SCHEMA['MovieTheater']))
            GRAPH.add((CINE_URI, MY_ONTOLOGY['name'], Literal(CINE_NAME, datatype=XSD.string)))

            for funcion in cine["Funciones"]:
                SALA = funcion["Sala"]
                string_name = 'ScreeningEvent' + '_' + CINE_NAME + '_' + SALA + '_' + MOVIE_NAME
                event_URI = MY_ONTOLOGY[string_name.replace(" ", "_")]
                GRAPH.add((event_URI, RDF.type, OWL.NamedIndividual))
                GRAPH.add((event_URI, RDF.type, SCHEMA['ScreeningEvent']))
                GRAPH.add((event_URI, SCHEMA['workPresented'], MOVIE_URI))
                GRAPH.add((event_URI, MY_ONTOLOGY['inLanguage'], Literal(funcion["Idioma"], datatype=XSD.string))) 
                for time in funcion["Hora"]:
                    GRAPH.add((event_URI, MY_ONTOLOGY['startTime'], Literal(datetime.strptime(time, '%H:%M'), datatype=XSD.dateTime)))
                GRAPH.add((CINE_URI, SCHEMA['event'], event_URI))

    with open(create_data_directory_path("individualsCinemalaplata" + ".ttl"),"w",encoding="utf-8") as file:
        file.write(GRAPH.serialize(format="turtle").decode("utf-8"))


if __name__ == "__main__":
    main()