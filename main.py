# main.py
import os
from fastapi import FastAPI
from api.chat_router import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

# Initialize the application instance
app = FastAPI()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origins],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.include_router(chat_router)


# Define a basic path operation
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
