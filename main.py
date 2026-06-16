from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from pydantic import BaseModel
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-prod")

class SignatureRequest(BaseModel):
    document_id: str
    signature_data: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/signature")
def sign_document(
    req: SignatureRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    return {
        "status": "signature_ok",
        "document_id": req.document_id,
        "user_id": user_id,
        "signature": req.signature_data[:20] + "..."
    }
