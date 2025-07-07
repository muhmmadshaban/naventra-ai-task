from fastapi import FastAPI, UploadFile, File
from backend.resume_parser import extract_jobs_from_resume
# from job_scraper import scrape_jobs
import os
import tempfile

app = FastAPI()

@app.post("/analyze-resume")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        suffix = resume.filename.split(".")[-1].lower()

        # Save the file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as temp_file:
            temp_file.write(await resume.read())
            temp_file_path = temp_file.name

        # Extract resume text using correct method
        if suffix == "pdf":
            import pdfplumber
            with pdfplumber.open(temp_file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif suffix == "docx":
            import docx
            doc = docx.Document(temp_file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif suffix == "txt":
            with open(temp_file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            return {"error": "Unsupported file type. Use .pdf, .docx, or .txt"}

        job_titles = extract_jobs_from_resume(text)
        # scraped_jobs = scrape_jobs(job_titles)
        return {"job_titles": job_titles, "jobs": "scraped_jobs"}

    except Exception as e:
        print(f"❌ Backend error: {e}")
        return {"error": str(e)}
