from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}

@app.get("/data")
def get_data():
    return {"data": ["Alice", "Bob", "Charlie"]}