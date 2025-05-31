import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
import re

# Load CSVs
authors_df = pd.read_csv("ABOX/authors.csv")
papers_df = pd.read_csv("ABOX/papers.csv")
venues_df = pd.read_csv("ABOX/venues.csv")
citations_df = pd.read_csv("ABOX/citations.csv")

# Initialize RDF graph and namespace
EX = Namespace("http://example.org/research/")
g = Graph()
g.bind("ex", EX)

# define the defeulat value for strings in integer fields
def safe_int(value, default=0):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
    
# Normalize otherAuthors column in papers_df ===
def normalize_author_list(field):
    if pd.isna(field) or not str(field).strip():
        return ""
    # Split by comma, semicolon, or mixed, and join with semicolon
    parts = re.split(r"[;,]\s*", str(field))
    return ";".join([p.strip() for p in parts if p.strip().isdigit()])

papers_df["otherAuthors"] = papers_df["otherAuthors"].apply(normalize_author_list)
papers_df["reviewers"] = papers_df["reviewers"].apply(normalize_author_list)


# === Authors ===
for _, row in authors_df.iterrows():
    author_uri = EX[f"author/{row['authorId']}"]
    g.add((author_uri, RDF.type, EX.Author))
    g.add((author_uri, EX.name, Literal(row['name'], datatype=XSD.string)))
    g.add((author_uri, EX.paperCount, Literal(safe_int(row['paper_Count']), datatype=XSD.integer)))

# === NEW Venues and Editions NEW ===
for _, row in venues_df.iterrows():
    venue_id = row["venueId"]
    venue_uri = EX[f"venue/{venue_id}"]
    venue_type = row["type"].capitalize()

    venue_label = row.get("venue")
    if pd.notna(venue_label):
        g.add((venue_uri, EX.name, Literal(venue_label, datatype=XSD.string)))

    # Declare the venue type (Conference, Workshop, or Journal)
    if venue_type in ["Conference", "Workshop", "Journal"]:
        g.add((venue_uri, RDF.type, EX[venue_type]))

    # === For Conferences and Workshops: create Editions and Proceedings ===
    if venue_type in ["Conference", "Workshop"]:
        edition_uri = EX[f"edition/{venue_id}-{row['year']}"]
        proceedings_uri = EX[f"proceedings/{venue_id}-{row['year']}"]

        g.add((edition_uri, RDF.type, EX.Edition))
        g.add((edition_uri, EX.heldInYear, Literal(int(row["year"]), datatype=XSD.gYear)))
        g.add((edition_uri, EX.isEditionOf, venue_uri))
        g.add((proceedings_uri, RDF.type, EX.Publication))
        g.add((edition_uri, EX.hasProceedings, proceedings_uri))  # Edition -> Proceedings

        # City handling
        if not pd.isna(row.get("city", None)):
            city_uri = EX[f"city/{re.sub(r'[^a-zA-Z0-9]', '', row['city'])}"]
            g.add((city_uri, RDF.type, EX.City))
            g.add((edition_uri, EX.heldIn, city_uri))
            g.add((city_uri, EX.hasCityName, Literal(row["city"], datatype=XSD.string)))

    # === For Journals: create Volumes ==
    elif venue_type == "Journal":
        #First clean the Volume String as it might make trouble
        raw_volume = str(row["volume"]).strip()
        clean_volume = re.sub(r"\s+", "-", raw_volume)  # replaces spaces with dash
        # Ende
        year = str(row["year"]).strip()
        

        if not pd.isna(row.get("volume", None)):
            volume_uri = EX[f"volume/{venue_id}-{year}-{clean_volume}"]
            g.add((volume_uri, RDF.type, EX.Volume))
            g.add((volume_uri, EX.hasVolumeNumber, Literal(str(row["volume"]), datatype=XSD.string)))
            g.add((volume_uri, EX.heldInYear, Literal(int(row["year"]), datatype=XSD.gYear)))
            g.add((venue_uri, EX.hasVolume, volume_uri))  # Journal -> Volume


# === Papers ===
for _, row in papers_df.iterrows():
    paper_uri = EX[f"paper/{row['paperId']}"]
    g.add((paper_uri, RDF.type, EX.Paper))
    g.add((paper_uri, EX.title, Literal(row["title"], datatype=XSD.string)))
    g.add((paper_uri, EX.year, Literal(int(row["year"]), datatype=XSD.gYear)))
    g.add((paper_uri, EX.abstract, Literal(row["abstract"], datatype=XSD.string)))
    g.add((paper_uri, EX.citationCount, Literal(int(row["citationCount"]), datatype=XSD.integer)))
    
## Here we link the paper and therefore its volume etc. properties to the right type of venue ###
    #First by striping the ids from the csv of any extras and blanks
    venue_type = row["venueType"].lower()
    paper_year = str(row["year"]).strip()
    paper_venue_id = str(row["venueId"]).strip()

    if venue_type in ["conference", "workshop"]:
        proceedings_uri = EX[f"proceedings/{row['venueId']}-{paper_year}"]
        g.add((paper_uri, EX.publishedIn, proceedings_uri))

    elif venue_type == "journal" and not pd.isna(row.get("volume", None)):
        raw_volume = str(row["volume"]).strip()
        clean_volume = re.sub(r"\s+", "-", raw_volume)
        volume_uri = EX[f"volume/{paper_venue_id}-{paper_year}-{clean_volume}"]
        g.add((paper_uri, EX.publishedIn, volume_uri))

## Here we assign the first author given in the csv #######
    for FirstAuthor_id in str(row["firstAuthor"]).replace(",", ";").split(";"):
        FirstAuthor_id = FirstAuthor_id.strip()
        if FirstAuthor_id:
            g.add((paper_uri, EX.hasCorrespondingAuthor, EX[f"author/{FirstAuthor_id}"]))

    # Here, we transform the list of other authors into seperate keys. 
    for CoAuthor_id in str(row["otherAuthors"]).replace(",", ";").split(";"):
        CoAuthor_id = CoAuthor_id.strip()
        if CoAuthor_id:
            g.add((paper_uri, EX.hasCoAuthor, EX[f"author/{CoAuthor_id}"]))

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
g.serialize(destination="abox_new.ttl", format="turtle")
print("ABox RDF file saved as 'abox_new.ttl'")