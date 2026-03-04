# docs/routes.py

from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException, File, status
from auth.routes import authenticate
from .vectorestore import load_vectorstore
import uuid

router = APIRouter()


@router.post("/upload_docs")
async def upload_docs(
    user=Depends(authenticate),
    file: UploadFile = File(...),
    role: str = Form(...),
):
    # Only admin can upload
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can upload files"
        )

    doc_id = str(uuid.uuid4())

    # ❗ No await (function is synchronous)
    load_vectorstore(file, role, doc_id)

    return {
        "message": "File uploaded successfully",
        "doc_id": doc_id,
        "accessible_to": role
    }
