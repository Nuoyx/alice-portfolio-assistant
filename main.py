# main.py
from fastapi import FastAPI
from api.chat_router import router as chat_router

# Initialize the application instance
app = FastAPI()
app.include_router(chat_router)


# Define a basic path operation
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/health")
async def health():
    return {"status": "ok"}
