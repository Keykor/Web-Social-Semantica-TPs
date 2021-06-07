from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.Wrapper import TURTLE, RDFXML
from rdflib.namespace import Namespace, RDF, OWL, RDFS
from rdflib import Graph, Literal
import time

SCHEMA = Namespace('https://schema.org/')
DBO = Namespace('http://dbpedia.org/ontology/')
MY_ONTOLOGY = Namespace('')
WDT = Namespace('http://www.wikidata.org/prop/direct/')
WD = Namespace('http://www.wikidata.org/entity/')

def obtenerNombres(g):
    literal_names = g.query("""
    SELECT ?person ?name
    WHERE {
        ?person a sch:Person.
        ?person :name ?name.
    }
    """)

    names = []
    for row in literal_names:
        names.append({'name': row[1].toPython(), 'uri': row[0].toPython()})

    return names

def consultarWikidata(g, name):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery("""
        CONSTRUCT {
        ?person ?predicate ?object
        }
        WHERE {
        ?person wdt:P31|wdt:P270 wd:Q5 .
        ?person ?label "%s" .
        ?person ?predicate ?object .
        }
    """ % name['name'])

    sparql.setReturnFormat(RDFXML)

    try:
        results = sparql.query().convert()
    except:
        time.sleep(60)
        results = sparql.query().convert()

    grafo = Graph().parse(data=results.serialize(format='xml'), format="xml", encoding="utf-8")

    for s, p, o in grafo.triples((None, WDT['P31'], WD['Q5'])):
        g.add((MY_ONTOLOGY[name['uri']], OWL.sameAs, s))
        print(str(s))

    for s, p, o in grafo.triples((None, None, None)):
        g.add((s, p, o))

    return

def consultarDBpedia(g, name):
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")

    sparql.setQuery("""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX schema: <http://schema.org/>

        CONSTRUCT {
        ?person ?predicate ?object
        }
        WHERE {
        ?person a dbo:Person .
        ?person dbo:birthName ?name .
        ?person ?predicate ?object .
        FILTER regex(?name, "%s")
        }
    """ % name['name'])

    sparql.setReturnFormat(TURTLE)

    try:
        results = sparql.query().convert()
    except:
        time.sleep(60)
        results = sparql.query().convert()
        
    grafo = Graph().parse(data=results, format="turtle", encoding="utf-8")

    for s, p, o in grafo.triples((None, RDF.type, DBO['Person'])):
        g.add((MY_ONTOLOGY[name['uri']], OWL.sameAs, s))
        print(str(s))
        pass

    for s, p, o in grafo.triples((None, None, None)):
        g.add((s, p, o))

    return

def main():
    g = Graph()
    g.parse('dataset-enriquecido.ttl', format="turtle", encoding="utf-8")

    names = obtenerNombres(g)

    for name in names:
        consultarWikidata(g, name)
        consultarDBpedia(g, name)

if __name__ == "__main__":
    main()