from step3_chat import embedder, collection

for q in ["can i pay rent in cash", "my landlord wants more rent, when will you tell me"]:
    res = collection.query(query_embeddings=embedder.encode([q]).tolist(), n_results=3)
    print("\nQ:", q)
    for d, dist in zip(res["documents"][0], res["distances"][0]):
        print(f"  {dist:.3f}  {d.splitlines()[0]}")