from rdflib import Graph, Namespace, RDF, URIRef
from SPARQLWrapper import SPARQLWrapper, JSON

# Namespaces
EX = Namespace("http://example.org/research/")
DBO = Namespace("http://dbpedia.org/ontology/")

# Create output graph
abox = Graph()
abox.bind("ex", EX)

# Query authors (scientists)
sparql_authors = SPARQLWrapper("http://localhost:7200/repositories/000111")
sparql_authors.setReturnFormat(JSON)
sparql_authors.setQuery("""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?author WHERE {
  ?author rdf:type dbo:Scientist .
}
LIMIT 50
""")
author_results = sparql_authors.query().convert()
authors = [URIRef(row["author"]["value"]) for row in author_results["results"]["bindings"]]

# Query papers (written works)
sparql_papers = SPARQLWrapper("http://localhost:7200/repositories/000111")
sparql_papers.setReturnFormat(JSON)
sparql_papers.setQuery("""
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT DISTINCT ?paper WHERE {
  ?paper rdf:type dbo:WrittenWork .
}
LIMIT 50
""")
paper_results = sparql_papers.query().convert()
papers = [URIRef(row["paper"]["value"]) for row in paper_results["results"]["bindings"]]

# Create triples
pair_count = min(len(authors), len(papers))
for i in range(pair_count):
    author = authors[i]
    paper = papers[i]

    abox.add((author, RDF.type, EX.Author))
    abox.add((paper, RDF.type, EX.Paper))
    abox.add((paper, EX.writes, author))

    if i == 0:
        abox.add((paper, EX.hasCorrespondingAuthor, author))

# Save to Turtle
abox.serialize("abox_from_dbpedia.ttl", format="turtle")
print("✅ ABOX file created: abox_from_dbpedia.ttl")