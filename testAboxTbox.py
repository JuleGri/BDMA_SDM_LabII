from rdflib import Graph, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import OWL

# Load TBox and ABox
tbox = Graph()
abox = Graph()

tbox.parse("TBOX/tbox.ttl", format="turtle")
abox.parse("ABOX/abox.ttl", format="turtle")

EX = Namespace("http://example.org/research/")

# === Extract Declared Classes and Properties from TBox ===
declared_classes = set()
declared_properties = set() 
domains = {}
ranges = {}

for s, p, o in tbox.triples((None, RDF.type, RDFS.Class)):
    declared_classes.add(s)

for s, p, o in tbox.triples((None, RDF.type, RDF.Property)):
    declared_properties.add(s)

for s, p, o in tbox.triples((None, RDFS.domain, None)):
    domains[s] = o

for s, p, o in tbox.triples((None, RDFS.range, None)):
    ranges[s] = o

# === Check Classes Used in ABox ===
used_classes = set(o for s, p, o in abox.triples((None, RDF.type, None)))

missing_classes = used_classes - declared_classes

# === Check Properties Used in ABox ===
used_properties = set(p for s, p, o in abox)

missing_properties = used_properties - declared_properties - {RDF.type}

# === Report ===
print("\n🔎 Missing Classes Used in ABox but Not Declared in TBox:")
for cls in sorted(missing_classes):
    print(f" - {cls}")

print("\n🔎 Properties Used in ABox but Not Declared in TBox:")
for prop in sorted(missing_properties):
    print(f" - {prop}")

# === Optional: Domain/Range Check
print("\n🔎 Domain/Range Inconsistencies (TBox Declared vs ABox Use):")

for s, p, o in abox:
    # Domain check
    expected_domain = domains.get(p)
    if expected_domain:
        inferred_types = set(abox.objects(s, RDF.type))
        if inferred_types and expected_domain not in inferred_types:
            print(f" ⚠ Domain mismatch for {p}: {s} is not a {expected_domain}")

    # Range check
    expected_range = ranges.get(p)
    if expected_range:
        inferred_types = set(abox.objects(o, RDF.type))
        if inferred_types and expected_range not in inferred_types:
            print(f" ⚠ Range mismatch for {p}: {o} is not a {expected_range}")
