import os
from sentence_transformers import SentenceTransformer
import chromadb
from openai import OpenAI

# ---------- SETTINGS (change these to switch AI provider) ----------
API_KEY = os.environ.get("LLM_API_KEY")
BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.groq.com/openai/v1")
MODEL = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")

# If the best matching chunk is farther than this, we do not trust it.
# Lower distance = more similar. Tune this number after testing.
MAX_DISTANCE = 0.80

if not API_KEY:
    raise SystemExit("Missing LLM_API_KEY. Set it in your terminal first (see instructions).")

# ---------- LOAD THE PIECES WE BUILT IN STEP 2 ----------
embedder = SentenceTransformer("all-MiniLM-L6-v2")
collection = chromadb.PersistentClient(path="./chroma_db").get_collection("faq")
llm = OpenAI(api_key=API_KEY, base_url=BASE_URL)

SYSTEM_PROMPT = (
    "You are a friendly customer support assistant for Palm Crest Properties. "
    "Answer ONLY using the CONTEXT provided. "
    "Include ALL relevant details from the context: numbers, fees, limits, "
    "conditions, exceptions, and time frames. "
    "Do not leave out any rule that applies to the question. "
    "If the context does not contain the answer, reply exactly: NOT_FOUND. "
    "Never invent prices, rules, or numbers."
    "Do not add facts or assumptions that are not stated in the context. "
)

HANDOFF = ("I'm not sure about that one. I'll connect you to a human agent: "
           "call 800-555-0100 (Sun-Thu, 9 AM - 6 PM).")


def answer(question):
    # 1. SEARCH: find the 3 most relevant chunks
    q_vec = embedder.encode([question]).tolist()
    res = collection.query(query_embeddings=q_vec, n_results=5)
    chunks, distances = res["documents"][0], res["distances"][0]

    # 2. SAFETY CHECK 1: is even the best match close enough?
    if distances[0] > MAX_DISTANCE:
        return HANDOFF, distances[0]

    # 3. GENERATE: give the AI the question and ONLY the retrieved chunks
    context = "\n\n".join(chunks)
    reply = llm.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"CONTEXT:\n{context}\n\nQUESTION: {question}"},
        ],
    ).choices[0].message.content.strip()

    # 4. SAFETY CHECK 2: did the AI say the context lacks the answer?
    if "NOT_FOUND" in reply:
        return HANDOFF, distances[0]
    return reply, distances[0]


if __name__ == "__main__":
    print("Palm Crest support bot. Type 'quit' to exit.\n")
    while True:
        q = input("You: ").strip()
        if q.lower() in ("quit", "exit"):
            break
        if not q:
            continue
        text, dist = answer(q)
        print(f"Bot: {text}   [distance: {dist:.3f}]\n")
