import os
import requests
import numpy as np
import jwt
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL")
GEMINI_GENERATIVE_MODEL = os.getenv("GEMINI_GENERATIVE_MODEL")
JWT_SECRET = os.getenv("JWT_SECRET")

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
embeddings_coll = db["embeddings"]

# FastAPI app
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class QueryRequest(BaseModel):
    query: str
    topK: int = 5

# JWT authentication
def authenticate(req: Request):
    auth = req.headers.get("authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("ownerId") or payload.get("sub") or payload.get("id")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# Cosine similarity
def cosine(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))

# Embedding function with error handling
def embed_text(text: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_EMBEDDING_MODEL}:embedContent"
    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
            json={"model": f"models/{GEMINI_EMBEDDING_MODEL}", "content": {"parts": [{"text": text}]}},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Embedding API request failed: {e}")
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Embedding API returned invalid JSON: {resp.text}")

    if "embedding" in data:
        return data["embedding"]["values"]
    raise HTTPException(status_code=500, detail=f"Bad embedding response: {data}")

# Gemini generative function with error handling
def generate_from_gemini(prompt: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_GENERATIVE_MODEL}:generateContent"
    
    # Corrected payload structure
    payload = {
        "system_instruction": {
            "parts": [
                {"text": "Answer using only CONTEXT. If not found, say so."}
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    try:
        resp = requests.post(
            url,
            headers={"Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY},
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Generative API request failed: {e}")
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Generative API returned invalid JSON: {resp.text}")

    if "candidates" in data:
        cand = data["candidates"][0]
        if "content" in cand:
            parts = cand["content"].get("parts")
            if parts:
                return " ".join([p.get("text", "") for p in parts if isinstance(p, dict)])
    return str(data)[:500]

# Main RAG endpoint
@app.post("/api/rag/query")
def rag_query(req: QueryRequest, request: Request):
    owner_id = authenticate(request)
    print(f"Authenticated owner ID: {owner_id}")

    # Get query embedding
    query_emb = embed_text(req.query)

    # Fetch all documents for this owner
    docs = list(embeddings_coll.find({"ownerId": owner_id}))
    print(f"Found {len(docs)} documents for owner ID: {owner_id}")

    scored = []
    for d in docs:
        emb = d.get("embeddingVector")
        if not emb:
            continue
        scored.append((cosine(query_emb, emb), d))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [d for _, d in scored[:req.topK]]
    
    print(f"Top documents retrieved: {len(top)}")
    
    # Prepare context
    context = "\n---\n".join([t.get("textChunk", "") for t in top])
    
    # If no context is found, return the "Not found" message
    if not context.strip():
        return {
            "answer": "Not found.",
            "sources": []
        }

    prompt = f"""
CONTEXT:
{context}

USER QUERY:
{req.query}
"""
    # Generate answer
    answer = generate_from_gemini(prompt)

    return {
        "answer": answer,
        "sources": [
            {
                "chunkId": t.get("chunkId"),
                "collection": t.get("sourceCollection"),
                "sourceId": t.get("sourceId"),
            } for t in top
        ]
    }