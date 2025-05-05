import requests


REPO_ID = "000111"
GRAPHDB_URL = f"http://localhost:7200/repositories/{REPO_ID}/statements"

# Mapping triples in Turtle format
mapping_ttl = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX ex: <http://example.org/research/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Class Mappings
dbo:Scientist rdfs:subClassOf ex:Author .
dbo:AcademicArticle rdfs:subClassOf ex:Paper .
dbo:WrittenWork rdfs:subClassOf ex:Paper .
dbo:Journal rdfs:subClassOf ex:Journal .
dbo:AcademicConference rdfs:subClassOf ex:Conference .
dbo:Conference rdfs:subClassOf ex:Conference .
dbo:Event rdfs:subClassOf ex:Edition .
dbo:Place rdfs:subClassOf ex:City .

# Property Mappings
dbo:abstract rdfs:subPropertyOf ex:hasAbstract .
dbo:author rdfs:subPropertyOf ex:writes .
dbo:editor rdfs:subPropertyOf ex:reviewedBy .
dbo:volume rdfs:subPropertyOf ex:hasVolume .
dc:subject rdfs:subPropertyOf ex:hasKeyword .
"""

# Upload as Turtle
response = requests.post(
    GRAPHDB_URL,
    headers={"Content-Type": "text/turtle"},
    data=mapping_ttl,
    params={"context": "<http://localhost:7200/mappings/>"}
)

# Response check
if response.status_code == 204:
    print("✅ Mapping triples uploaded successfully to GraphDB.")
else:
    print(f"❌ Failed to upload mappings: {response.status_code}\n{response.text}")