import json

# Read topics
with open("tinysteps-data/topics/topics.json", "r") as f:
    topics_data = json.load(f)

vocab_refs = {}
grammar_refs = {}

for topic in topics_data["topics"]:
    for spiral in topic["spiral"]:
        level = spiral["level"]
        vocab_ids = spiral.get("vocabulary_ids", [])
        grammar_ids = spiral.get("grammar_ids", [])
        
        if level not in vocab_refs:
            vocab_refs[level] = []
        if level not in grammar_refs:
            grammar_refs[level] = []
            
        vocab_refs[level].extend(vocab_ids)
        grammar_refs[level].extend(grammar_ids)

# Write report
with open("tinysteps-data/scratch_report.txt", "w") as f:
    f.write("=== VOCABULARY REFERENCES IN TOPICS.JSON ===\n")
    for lvl in ["starters", "movers", "flyers", "ket", "pet"]:
        refs = sorted(list(set(vocab_refs.get(lvl, []))))
        f.write(f"{lvl}: {len(refs)} unique references. Min ID: {refs[0] if refs else None}, Max ID: {refs[-1] if refs else None}\n")
        f.write(f"All: {', '.join(refs)}\n\n")
        
    f.write("=== GRAMMAR REFERENCES IN TOPICS.JSON ===\n")
    for lvl in ["starters", "movers", "flyers", "ket", "pet"]:
        refs = sorted(list(set(grammar_refs.get(lvl, []))))
        f.write(f"{lvl}: {len(refs)} unique references. Min ID: {refs[0] if refs else None}, Max ID: {refs[-1] if refs else None}\n")
        f.write(f"All: {', '.join(refs)}\n\n")
