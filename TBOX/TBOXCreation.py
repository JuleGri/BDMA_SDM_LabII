from rdflib import Graph, Namespace, RDF, RDFS, URIRef

# Define namespace
EX = Namespace("http://example.org/research/")

# Initialize graph
g = Graph()
g.bind("ex", EX)
g.bind("rdfs", RDFS)

# === Class definitions ===
classes = [
    "Author", "Reviewer", "Paper", "Review", "Keyword",
    "City", "Edition", "Volume", "Publication",
    "Conference", "Workshop", "Journal"
]

for cls in classes:
    g.add((EX[cls], RDF.type, RDFS.Class))

# Subclass relationships
g.add((EX["Reviewer"], RDFS.subClassOf, EX["Author"]))
g.add((EX["Conference"], RDFS.subClassOf, EX["Publication"]))
g.add((EX["Workshop"], RDFS.subClassOf, EX["Publication"]))
g.add((EX["Journal"], RDFS.subClassOf, EX["Publication"]))

# === Property definitions with domain and range ===
properties = {
    "writes": ("Author", "Paper"),
    "hasCorrespondingAuthor": ("Paper", "Author"),
    "hasCoAuthor": ("Paper", "Author"),
    "publishedIn": ("Paper", "Publication"),
    "hasReview": ("Paper", "Review"),
    "reviewedBy": ("Review", "Reviewer"),
    "hasAbstract": ("Paper", None),
    "hasKeyword": ("Paper", "Keyword"),
    "cites": ("Paper", "Paper"),
    "hasEdition": ("Publication", "Edition"),
    "heldIn": ("Edition", "City"),
    "heldInYear": ("Edition", None),
    "hasVolume": ("Journal", "Volume"),
    "volumeYear": ("Volume", None)
}

for prop, (domain, range_) in properties.items():
    prop_uri = EX[prop]
    g.add((prop_uri, RDF.type, RDF.Property))
    if domain:
        g.add((prop_uri, RDFS.domain, EX[domain]))
    if range_:
        g.add((prop_uri, RDFS.range, EX[range_]))

# Save TBOX
g.serialize("tbox.ttl", format="turtle")
print("TBOX saved as 'tbox.ttl'")
