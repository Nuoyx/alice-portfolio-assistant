# main.py
import os
from fastapi import FastAPI, Request
from api.chat_router import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Initialize the application instance
app = FastAPI()

allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "response": "Please enter a message between 1 and 1000 characters."
        },
    )

