from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .models import SignupRequest
from auth.hash_utils import hash_password, verify_password

from config.db import collection

router = APIRouter()
 

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    user = collection.find_one({"username": credentials.username})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"username": user["username"], "role": user["role"]}




  



@router.post("/signup")
async def signup(request:SignupRequest):
    if collection.find_one({"username": request.username}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    hashed_password = hash_password(request.password)
    user = {"username": request.username, "password": hashed_password, "role": request.role}
    collection.insert_one(user)
    return {"message": "User created successfully"}





@router.get("/login")
def login(user=Depends(authenticate)):
    return {"message": f"welcome {user['username']}","role":user["role"]}

