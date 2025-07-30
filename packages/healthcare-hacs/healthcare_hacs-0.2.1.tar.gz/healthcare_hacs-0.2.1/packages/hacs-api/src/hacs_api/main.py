from fastapi import FastAPI

app = FastAPI(title="HACS API", version="0.1.0")


@app.get("/")
def root():
    return {"message": "HACS API Service"}
