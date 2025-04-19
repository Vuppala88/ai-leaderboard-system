from fastapi import FastAPI, File, UploadFile
import json
import nbformat
import subprocess
import os
import aiofiles
import subprocess
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/submit-notebook")
async def upload_notebook(file: UploadFile):
    file_path = f"uploads/{file.filename}"

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(await file.read())

    # Extract F1-scores from the uploaded notebook
    f1_scores = extract_f1_from_notebook(file_path)

    # Save scores for ZKP proof generation
    with open("f1_scores.json", "w") as f:
        json.dump(f1_scores, f)

    return {"message": "Notebook processed successfully!", "f1_scores": f1_scores}

def extract_f1_from_notebook(notebook_path):
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    extracted_scores = {"f1_c45": None, "f1_cart": None}

    for cell in nb.cells:
        if cell.cell_type == "code" and "f1_score" in cell.source:
            exec(cell.source, globals())
            extracted_scores["f1_c45"] = round(globals().get("f1_c45", 0) * 10000)
            extracted_scores["f1_cart"] = round(globals().get("f1_cart", 0) * 10000)

    return extracted_scores

@app.post("/generate-proof")
async def generate_zkp():
    def generate_proof():
    with open("f1_scores.json", "r") as f:
        scores = json.load(f)

    # Run ZoKrates commands
    subprocess.run("zokrates compile -i f1_verification.zok", shell=True)
    subprocess.run("zokrates setup", shell=True)
    subprocess.run(f"zokrates compute-witness -a {scores['f1_c45']} {scores['f1_cart']}", shell=True)
    subprocess.run("zokrates generate-proof", shell=True)

    return "ZKP proof generated successfully!"

    # Load F1-scores
    with open("f1_scores.json", "r") as f:
        scores = json.load(f)

    # Append verified result to leaderboard
    leaderboard_entry = {
        "name": "Model Submission",
        "f1_c45": scores["f1_c45"] / 10000,
        "f1_cart": scores["f1_cart"] / 10000,
        "is_verified": True
    }

    # Update leaderboard
    leaderboard_path = "leaderboard.json"
    leaderboard = []
    if os.path.exists(leaderboard_path):
        with open(leaderboard_path, "r") as f:
            leaderboard = json.load(f)

    leaderboard.append(leaderboard_entry)

    with open(leaderboard_path, "w") as f:
        json.dump(leaderboard, f, indent=4)

    return {"message": message, "leaderboard_updated": True}

@app.get("/validate-proof")
async def validate_proof():
    proof_path = "zokrates/proof.json"

    if not os.path.exists(proof_path):
        return {"message": "Error: Proof file not found!", "is_valid": False}

    # Run ZoKrates verification command
    is_valid = subprocess.run("zokrates verify", shell=True).returncode == 0
    return {"message": "Proof validation complete!", "is_valid": is_valid}

@app.get("/leaderboard")
async def get_leaderboard():
    with open("leaderboard.json", "r") as f:
        leaderboard = json.load(f)
    return leaderboard