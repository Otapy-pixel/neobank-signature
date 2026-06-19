from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import os
from datetime import datetime, timedelta

app = FastAPI(title="Néobanque Signature API")

# CORS pour Flutter Web + Mobile + FlutterFlow
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod mets l’URL de ton app FlutterFlow
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("JWT_SECRET", "change-moi-en-prod-urgent")
ALGORITHM = "HS256"

class SignatureRequest(BaseModel):
    user_id: str
    document_hash: str

@app.get("/")
def health():
    return {"status": "API Néobanque OK", "time": datetime.now().isoformat()}

@app.post("/signer")
def signer_document(data: SignatureRequest):
    """Génère une signature JWT pour un document"""
    payload = {
        "user_id": data.user_id,
        "doc_hash": data.document_hash,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta
        (hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"signature": token, "status": "signé"}

@app.post("/verifier")
def verifier_signature(token: str):
    """Vérifie si la signature JWT est valide"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valide": True, "data": payload}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature expirée")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Signature invalide")
