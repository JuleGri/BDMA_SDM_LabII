import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
import re

# Load CSVs
authors_df = pd.read_csv("authors.csv")
papers_df = pd.read_csv("papers.csv")
venues_df = pd.read_csv("venues.csv")
citations_df = pd.read_csv("citations.csv")

# Initialize RDF graph and namespace
EX = Namespace("http://example.org/research/")
g = Graph()
g.bind("ex", EX)

def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

# === Authors ===
for _, row in authors_df.iterrows():
    author_uri = EX[f"author/{row['authorId']}"]
    g.add((author_uri, RDF.type, EX.Author))
    g.add((author_uri, EX.name, Literal(row['name'], datatype=XSD.string)))
    g.add((author_uri, EX.paperCount, Literal(safe_int(row['paper_Count']), datatype=XSD.integer)))
    try:
        for aff in eval(row['affiliations']):
            g.add((author_uri, EX.affiliatedWith, Literal(aff, datatype=XSD.string)))
    except:
        pass

# === Venues and Editions ===
for _, row in venues_df.iterrows():
    venue_id = row["venueId"]
    venue_uri = EX[f"venue/{venue_id}"]
    edition_uri = EX[f"edition/{venue_id}-{row['year']}"]

    venue_type = row["type"].capitalize()
    if venue_type in ["Journal", "Conference", "Workshop"]:
        g.add((venue_uri, RDF.type, EX[venue_type]))

    g.add((edition_uri, RDF.type, EX.Edition))
    g.add((edition_uri, EX.heldInYear, Literal(int(row["year"]), datatype=XSD.gYear)))
    g.add((edition_uri, EX.isEditionOf, venue_uri))

    if not pd.isna(row.get("city", None)):
        city_uri = EX[f"city/{re.sub(r'[^a-zA-Z0-9]', '', row['city'])}"]
        g.add((city_uri, RDF.type, EX.City))
        g.add((edition_uri, EX.heldIn, city_uri))
        g.add((city_uri, EX.hasCityName, Literal(row["city"], datatype=XSD.string)))

    if venue_type == "Journal" and not pd.isna(row.get("volume", None)):
        volume_uri = EX[f"volume/{venue_id}-{row['volume']}"]
        g.add((volume_uri, RDF.type, EX.Volume))
        g.add((venue_uri, EX.hasVolume, volume_uri))

# === Papers ===
for _, row in papers_df.iterrows():
    paper_uri = EX[f"paper/{row['paperId']}"]
    g.add((paper_uri, RDF.type, EX.Paper))
    g.add((paper_uri, EX.title, Literal(row["title"], datatype=XSD.string)))
    g.add((paper_uri, EX.year, Literal(int(row["year"]), datatype=XSD.gYear)))
    g.add((paper_uri, EX.abstract, Literal(row["abstract"], datatype=XSD.string)))
    g.add((paper_uri, EX.citationCount, Literal(int(row["citationCount"]), datatype=XSD.integer)))
    

    edition_uri = EX[f"edition/{row['venueId']}-{row['year']}"]
    g.add((paper_uri, EX.publishedIn, edition_uri))

    g.add((paper_uri, EX.hasAuthor, EX[f"author/{row['firstAuthor']}"]))

    # Here, we transform the list of other authors into seperate keys. 
    for author_id in str(row["otherAuthors"]).split(";"):
        author_id = author_id.strip()
        if author_id:
            g.add((paper_uri, EX.hasAuthor, EX[f"author/{author_id}"]))

    # Here, we transform the list of reviewers into seperate keys.
    for reviewer_id in str(row.get("reviewers", "")).split(";"):
        reviewer_id = reviewer_id.strip()
        if reviewer_id:
            g.add((paper_uri, EX.reviewedBy, EX[f"author/{reviewer_id}"]))

# Citations
for _, row in citations_df.iterrows():
    citing = EX[f"paper/{row['citingPaperId']}"]
    cited = EX[f"paper/{row['citedPaperId']}"]
    g.add((citing, EX.cites, cited))

# Save ABox to TTL format
g.serialize(destination="abox.ttl", format="turtle")
print("ABox RDF file saved as 'abox.ttl'")