from fastapi import APIRouter,Depends,UploadFile,Form,HTTPException,File,status
from auth.routes import authenticate
from .vectorestore import load_vectoresrore
import uuid

router = APIRouter()

@router.post("/upload_docs")
def upload_docs(
    user=Depends(authenticate),
    file:UploadFile=File(...),
    role:str =Form(...),
    
):
    if user ["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="only admin can upload file")
    doc_id = str(uuid.uuid4())
    load_vectoresrore([file],role,doc_id)
    return {"message": "File uploaded successfully","doc_id":doc_id,"accessible to":role}
    
