from sentence_transformers import SentenceTransformer
import chromadb

# ---------- 1. CHUNKING ----------
# Each Q&A pair is separated by a blank line, so we split on blank lines.
with open("company_faq.txt", "r", encoding="utf-8") as f:
    text = f.read()

chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
print(f"Created {len(chunks)} chunks")

# ---------- 2. EMBEDDINGS ----------
# This model turns each chunk into a list of 384 numbers that capture its meaning.
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks).tolist()

# ---------- 3. STORE IN VECTOR DATABASE ----------
client = chromadb.PersistentClient(path="./chroma_db")
# Delete the old collection if it exists, so re-running does not create duplicates.
try:
    client.delete_collection("faq")
except Exception:
    pass
collection = client.create_collection(name="faq", metadata={"hnsw:space": "cosine"})

collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings,
)
print("Stored all chunks in the database")

# ---------- 4. TEST THE SEARCH ----------
question = "Can I bring my dog to the apartment?"
q_embedding = model.encode([question]).tolist()
results = collection.query(query_embeddings=q_embedding, n_results=2)

print("\nQuestion:", question)
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    print(f"\nDistance: {dist:.3f}")
    print(doc)
