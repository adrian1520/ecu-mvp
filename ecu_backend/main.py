import os
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile

from workflow import run_workflow

app = FastAPI()

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def root():
    return {"status": "ECU Backend Online"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".bin"):
        raise HTTPException(status_code=400, detail="Only .bin files allowed")

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.bin")

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    return {"file_id": file_id, "filename": file.filename, "size": len(content)}


@app.post("/analyze/{file_id}")
def analyze_file(file_id: str):
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.bin")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    with open(file_path, "rb") as f:
        content = f.read()

    result = run_workflow(content)
    result["file_id"] = file_id

    return result
