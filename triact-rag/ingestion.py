import os
import json
import uuid
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
embeddings_coll = db["embeddings"]

def chunk_text(text, max_chars=2800):
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        last_period = text.rfind(". ", start, end)
        if last_period > start:
            end = last_period + 1
        chunks.append(text[start:end].strip())
        start = end
    return [c for c in chunks if c]

def embed_text_batch(texts):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_EMBEDDING_MODEL}:embedContent"
    resp = requests.post(
        url,
        headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
        json={"model": f"models/{GEMINI_EMBEDDING_MODEL}", "content": {"parts": [{"text": t} for t in texts]}},
        timeout=60,
    )
    data = resp.json()
    if "embeddings" in data:
        return [e.get("values") for e in data["embeddings"]]
    raise RuntimeError(f"Bad embedding response: {json.dumps(data)[:300]}")

def ingest_collection(col_name):
    col = db[col_name]
    for doc in col.find({}):
        owner_id = doc.get("ownerId") or doc.get("owner") or doc.get("shopId")
        if not owner_id:
            continue

        parts = [f"_source_collection_: {col_name}"]
        for k, v in doc.items():
            if k == "_id":
                continue
            try:
                parts.append(f"{k}: {json.dumps(v)}" if isinstance(v, (dict, list)) else f"{k}: {v}")
            except:
                parts.append(f"{k}: (unserializable)")
        text = "\n".join(parts)

        chunks = chunk_text(text)
        embeddings = embed_text_batch(chunks)
        for chunk, emb in zip(chunks, embeddings):
            embeddings_coll.update_one(
                {"ownerId": owner_id, "chunkId": str(uuid.uuid4())},
                {"$set": {
                    "ownerId": owner_id,
                    "textChunk": chunk,
                    "embeddingVector": emb,
                    "sourceCollection": col_name,
                    "sourceId": str(doc["_id"]),
                }},
                upsert=True,
            )
        print(f"Ingested {len(chunks)} chunks from {col_name} doc {doc['_id']}")

def main():
    for c in ["invoices", "sales", "stock"]:
        ingest_collection(c)
    print("✅ Ingestion complete")

if __name__ == "__main__":
    main()