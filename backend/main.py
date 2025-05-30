# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os

from zip_utils import save_and_extract_zip, extract_code_from_folder
from git_utils import clone_repo
from ai_engine import generate_documentation

app = FastAPI()

# Enable CORS for frontend testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs("uploads", exist_ok=True)

@app.post("/generate-docs/")
async def generate_docs(
    file: UploadFile = File(None),
    github_url: str = Form(None)
):
    # Handle GitHub URL cloning or ZIP upload
    if github_url:
        folder_path = clone_repo(github_url)
    elif file:
        folder_path = save_and_extract_zip(file)
    else:
        return {"error": "No input provided"}

    # Extract and process code
    code_text = extract_code_from_folder(folder_path)
    documentation = generate_documentation(code_text)

    return {"markdown": documentation}
