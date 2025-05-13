from graphviz import Digraph

# Initialize the graph
dot = Digraph(comment="TBOX: Research Ontology")

# === Classes (Nodes) ===
classes = [
    "Author", "Reviewer", "Paper", "Review", "Keyword",
    "City", "Edition", "Volume", "Publication",
    "Conference", "Workshop", "Journal"
]

# Add each class as a node
for cls in classes:
    dot.node(cls, cls)

# === Subclass relationships ===
dot.edge("Reviewer", "Author", label="subClassOf")
dot.edge("Conference", "Publication", label="subClassOf")
dot.edge("Workshop", "Publication", label="subClassOf")
dot.edge("Journal", "Publication", label="subClassOf")

# === Property relationships (edges between class nodes) ===
properties = [
    ("Author", "Paper", "writes"),
    ("Paper", "Author", "hasCorrespondingAuthor"),
    ("Paper", "Author", "hasCoAuthor"),
    ("Paper", "Publication", "publishedIn"),
    ("Paper", "Review", "hasReview"),
    ("Review", "Reviewer", "reviewedBy"),
    ("Paper", "Keyword", "hasKeyword"),
    ("Paper", "Paper", "cites"),
    ("Publication", "Edition", "hasEdition"),
    ("Edition", "City", "heldIn"),
    ("Edition", "Year", "heldInYear"),  # Literal-type placeholder
    ("Journal", "Volume", "hasVolume")
]

# Add edges for all properties
for source, target, label in properties:
    dot.edge(source, target, label=label)

# === Save the diagram ===
# Change the output path if needed
output_path = "tbox_diagram"
dot.render(output_path, format="png", cleanup=True)

print(f"✅ Diagram saved as {output_path}.png")
