import json
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
import os

# === Load JSON files ===
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

papers = load_json("ABOX/papers.json")
authors = load_json("ABOX/authors.json")
venues = load_json("ABOX/venues.json")
citations = load_json("ABOX/citations.json")

# === Setup RDF graph ===
EX = Namespace("http://example.org/semantics/")
g = Graph()
g.bind("ex", EX)

# === Add Venue Nodes ===
for venue in venues:
    venue_uri = EX[f"venue/{venue['venueId']}"]
    g.add((venue_uri, RDF.type, EX.Venue))
    g.add((venue_uri, EX.name, Literal(venue['venue'], datatype=XSD.string)))
    g.add((venue_uri, EX.year, Literal(venue['year'], datatype=XSD.gYear)))
    g.add((venue_uri, EX.venueType, Literal(venue['type'], datatype=XSD.string)))
    if venue.get("volume"):
        g.add((venue_uri, EX.volume, Literal(venue["volume"], datatype=XSD.string)))
    if venue.get("city"):
        g.add((venue_uri, EX.city, Literal(venue["city"], datatype=XSD.string)))

# === Add Author Nodes ===
for author in authors:
    author_uri = EX[f"author/{author['authorId']}"]
    g.add((author_uri, RDF.type, EX.Author))
    g.add((author_uri, EX.name, Literal(author['name'], datatype=XSD.string)))
    g.add((author_uri, EX.hIndex, Literal(author['hIndex'], datatype=XSD.integer)))
    g.add((author_uri, EX.paperCount, Literal(author['paper_Count'], datatype=XSD.integer)))
    for aff in author.get("affiliations", []):
        g.add((author_uri, EX.affiliatedWith, Literal(aff, datatype=XSD.string)))

# === Add Paper Nodes and Author Links ===
for paper in papers:
    paper_uri = EX[f"paper/{paper['paperId']}"]
    g.add((paper_uri, RDF.type, EX.Paper))
    g.add((paper_uri, EX.title, Literal(paper['title'], datatype=XSD.string)))
    g.add((paper_uri, EX.year, Literal(paper['year'], datatype=XSD.gYear)))
    g.add((paper_uri, EX.abstract, Literal(paper.get('abstract', ""), datatype=XSD.string)))
    g.add((paper_uri, EX.citationCount, Literal(paper.get('citationCount', 0), datatype=XSD.integer)))
    g.add((paper_uri, EX.influentialCitations, Literal(paper.get('influentialCitationCount', 0), datatype=XSD.integer)))

    # Optional volume and pages
    if paper.get("volume") and paper.get("volume") != "N/A":
        g.add((paper_uri, EX.volume, Literal(paper["volume"], datatype=XSD.string)))
    if paper.get("pages") and paper.get("pages") != "N/A":
        g.add((paper_uri, EX.pages, Literal(paper["pages"], datatype=XSD.string)))

    # Venue link
    venue_id = paper["venueId"]
    venue_uri = EX[f"venue/{venue_id}"]
    g.add((paper_uri, EX.publishedIn, venue_uri))

    # Author links
    if paper.get("firstAuthor"):
        g.add((paper_uri, EX.hasAuthor, EX[f"author/{paper['firstAuthor']}"]))
    for aid in paper.get("otherAuthors", []):
        g.add((paper_uri, EX.hasAuthor, EX[f"author/{aid}"]))

    # Reviewers
    for rid in paper.get("reviewers", []):
        g.add((paper_uri, EX.reviewedBy, EX[f"author/{rid}"]))

# === Add Citation Relationships ===
for citation in citations:
    citing = citation.get("citingPaperId")
    cited = citation.get("citedPaperId")
    if citing and cited:
        citing_uri = EX[f"paper/{citing}"]
        cited_uri = EX[f"paper/{cited}"]
        g.add((citing_uri, EX.cites, cited_uri))

# === Save RDF Graph ===
output_path = "knowledge_graph.ttl"
g.serialize(destination=output_path, format="turtle")
print(f"✅ RDF graph saved to: {output_path}")
