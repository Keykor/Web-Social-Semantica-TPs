from SPARQLWrapper import SPARQLWrapper
from SPARQLWrapper.Wrapper import RDFXML
from rdflib.namespace import Namespace, RDF, OWL
from rdflib import Graph
import time

SCHEMA = Namespace('https://schema.org/')
DBO = Namespace('http://dbpedia.org/ontology/')
MY_ONTOLOGY = Namespace('')
WDT = Namespace('http://www.wikidata.org/prop/direct/')
WD = Namespace('http://www.wikidata.org/entity/')

def consultarWikidata(g):
    people = []
    for s, p, o in g.triples((None, WDT['P31'], WD['Q5'])):
        people.append(s)        

    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

    sparql.setQuery("""
        CONSTRUCT {
            ?directed <wasDirectedByOscarWinner> ?director 
        }
        WHERE {
            ?director wdt:P31 wd:Q5.
            ?director wdt:P166 ?award.
            ?award wdt:P361 wd:Q19020.
            ?film wdt:P31 wd:Q11424.
            ?film wdt:P57 ?director.
            ?film wdt:P161 ?directed.
            ?directed wdt:P31 wd:Q5.
        }
    """)

    sparql.setReturnFormat(RDFXML)

    try:
        results = sparql.query().convert()
    except:
        time.sleep(60)
        results = sparql.query().convert()

    grafoConsulta = Graph().parse(data=results.serialize(format='xml'), format="xml", encoding="utf-8")
    
    for s, p, o in grafoConsulta.triples((None, None, None)):
        if (s in people) and (o in people):
            print(str(s))
            print(str(o))
            print('----------')
            g.add((s, MY_ONTOLOGY['wasDirectedByOscarWinner'], o))
            pass

    return


def main():
    g = Graph()
    g.parse('output.ttl', format="turtle", encoding="utf-8")

    #agrega la propiedad wasDirectedByOscarWinner a la ontología
    g.add((MY_ONTOLOGY['wasDirectedByOscarWinner'], RDF.type, OWL.ObjectProperty))

    consultarWikidata(g)

    print(g.serialize(format="turtle").decode("utf-8"))

if __name__ == "__main__":
    main()