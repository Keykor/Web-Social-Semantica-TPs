import requests
import rdflib
from rdflib.namespace import OWL

g = rdflib.Graph()

#print(r.text)
#result = g.parse("https://raw.githubusercontent.com/Keykor/Web-Social-Semantica-TPs/main/cohort.ttl", format="turtle")
#result = g.parse("galgadot.ttl", format="turtle", encoding="utf-8")
#g.parse(data=r.text, format="turtle", encoding="utf-8")
g.parse("links.ttl", format="turtle", encoding="utf-8")

links = []
for s, p, o in g.triples((None, OWL.sameAs, None)):
    links.append(o)

g.parse("dataset-original.ttl", format="turtle", encoding="utf-8")

for link in links:
    r = requests.get(link, headers={'Accept': 'text/turtle'})
    g.parse(data=r.text, format="turtle", encoding="utf-8")

with open("dataset-enriquecido.ttl","w",encoding="utf-8") as file:
    file.write(g.serialize(format="turtle").decode("utf-8"))
