# backend/main.py

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from auth_utils import authenticate_user, create_access_token, verify_token
from zip_utils import save_and_extract_zip, extract_code_from_folder
from git_utils import clone_repo
from ai_engine import generate_documentation
from export_utils import export_to_pdf, export_to_docx, export_to_md
from github_push_utils import push_docs_to_github
from db_utils import init_db, log_session 
import traceback



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

@app.on_event("startup")
async def startup_event():
    init_db()  # 🆕 initialize DB on startup

@app.post("/generate-docs/")
async def generate_docs(
    file: UploadFile = File(None),
    github_url: str = Form(None),
    current_user: str = Depends(verify_token)
):
    request_id = str(uuid.uuid4())  # 🆕 generate unique request ID
    try:
        # Handle GitHub URL cloning or ZIP upload
        if github_url:
            print("🔗 Cloning from GitHub...")
            folder_path = clone_repo(github_url)
            source = github_url
        elif file:
            print("📦 Extracting ZIP file...")
            folder_path = save_and_extract_zip(file)
            source = file.filename
        else:
            return {"error": "No input provided"}

        # Extract and process code
        print("📂 Parsing code files...")
        code_text = extract_code_from_folder(folder_path)

        print("🤖 Generating documentation...")
        documentation = generate_documentation(code_text)

        # Generate exports
        md_path = export_to_md(documentation)
        pdf_path = export_to_pdf(documentation)
        docx_path = export_to_docx(documentation)

        # 🆕 Log session
        log_session(request_id, source, "success", datetime.utcnow().isoformat())

        return {
            "request_id": request_id,
            "markdown": documentation,
            "downloads": {
                "md": md_path,
                "pdf": pdf_path,
                "docx": docx_path
            }
        }

    except Exception as e:
        print("❌ ERROR:", e)
        error_trace = traceback.format_exc()
        print("❌ ERROR:\n", error_trace)

        log_session(request_id, github_url or (file.filename if file else "unknown"), "error", datetime.utcnow().isoformat(), str(e))
        return {"error": str(e), "request_id": request_id}

@app.post("/push-docs/")
async def push_docs(
    github_token: str = Form(...),
    repo_name: str = Form(...),
    branch: str = Form("main"),
    path: str = Form("docs.md"),
    current_user: str = Depends(verify_token)
):
    
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to push docs")
    
    request_id = str(uuid.uuid4())
    try:
        with open("uploads/output.md", "r") as f:
            markdown_text = f.read()

        result = push_docs_to_github(github_token, repo_name, markdown_text, branch, path)

        # 🆕 Log push
        log_session(request_id, repo_name, "push_success", datetime.utcnow().isoformat())

        return {"status": result, "request_id": request_id}

    except Exception as e:
        print("❌ GitHub push failed:", e)
        error_trace = traceback.format_exc()
        print("❌ GitHub push failed:\n", error_trace)

        log_session(request_id, repo_name, "push_error", datetime.utcnow().isoformat(), str(e))
        return {"error": str(e), "request_id": request_id}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token(data={"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}
