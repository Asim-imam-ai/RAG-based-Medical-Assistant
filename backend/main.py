from fastapi import FastAPI
from auth.routes import router as auth_routher
from docs.routes import router as docs_routher
from chat.routes import router as chat_routher
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize once
app = FastAPI(title="Medical Assistant API")

# 2. Include your external routes
app.include_router(auth_routher)
app.include_router(docs_routher)
app.include_router(chat_routher)

# 3. Add any local routes to the SAME 'app' instance
@app.get("/")
async def root():
    return {"message": "Hello World"}
