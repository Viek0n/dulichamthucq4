from fastapi import FastAPI

app = FastAPI(title="My Project API")


@app.get("/")
def root():
    return {"status": "ok"}