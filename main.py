from fastapi import FastAPI, UploadFile, File
from workflow import run_workflow

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ECU MVP Online"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    result = run_workflow(content)
    return result