# main.py
from fastapi import FastAPI

# Initialize the application instance
app = FastAPI()

# Define a basic path operation
@app.get("/")
def read_root():
    return {"Hello": "World"}

