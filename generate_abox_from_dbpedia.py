from rdflib import Graph, Namespace, RDF, URIRef, Literal
from SPARQLWrapper import SPARQLWrapper, JSON

# SPARQL connection to GraphDB
sparql = SPARQLWrapper("http://localhost:7200/repositories/000111")
sparql.setReturnFormat(JSON)

# Namespaces
EX = Namespace("http://example.org/research/")
DBO = Namespace("http://dbpedia.org/ontology/")

# Output graph
abox = Graph()
abox.bind("ex", EX)

# Step 1: Get authors (DBpedia scientists)
sparql.setQuery("""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?author WHERE {
  ?author rdf:type dbo:Scientist .
}
LIMIT 50
""")
author_results = sparql.query().convert()

# Add authors to ABOX
for row in author_results["results"]["bindings"]:
    uri = URIRef(row["author"]["value"])
    abox.add((uri, RDF.type, EX.Author))

# Step 2: Get papers and abstracts
sparql.setQuery("""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?paper ?abstract WHERE {
  ?paper rdf:type dbo:WrittenWork ;
         dbo:abstract ?abstract .
  FILTER(lang(?abstract) = "en")
}
LIMIT 50
""")
paper_results = sparql.query().convert()

# Add papers to ABOX
for row in paper_results["results"]["bindings"]:
    uri = URIRef(row["paper"]["value"])
    abstract = Literal(row["abstract"]["value"], lang="en")
    abox.add((uri, RDF.type, EX.Paper))
    abox.add((uri, EX.hasAbstract, abstract))

# Step 3: Save ABOX
abox.serialize("abox_from_dbpedia.ttl", format="turtle")
print("ABOX file created: abox_from_dbpedia.ttl")