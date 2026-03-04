from fastapi import APIRouter, Depends, Form
from auth.routes import authenticate
from .chat_query import answer_query  # Changed: removed get_response

router = APIRouter()

# @router.post("/chat")
# async def chat(user=Depends(authenticate), message: str = Form(...)):
#     # Changed: call answer_query instead of get_response
#     response = await answer_query(message, user["role"])
#     return {"response": response}


@router.post("/chat")
async def chat(user=Depends(authenticate), message: str = Form(...)):
    response = await answer_query(message, user["role"])
    # Change "response" to "answer" to match your Streamlit code
    return {"answer": response}