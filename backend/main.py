from fastapi import FastAPI, UploadFile, File, Request
from backend.resume_parser import extract_jobs_from_resume
from backend.internshala_scraper import fetch_both_internships_and_jobs 
from backend.auto_apply_internshala import auto_apply

import tempfile
import os
import json
import logging
import csv
from datetime import datetime

# === Setup logging ===
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_file_path = os.path.join(LOG_DIR, "resume_analysis.log")

logging.basicConfig(
    filename=log_file_path,
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# === Initialize FastAPI ===
app = FastAPI()


# === STEP 1: Extract Job Titles from Resume ===
@app.post("/analyze-resume")
async def analyze_resume(resume: UploadFile = File(...)):
    try:
        suffix = resume.filename.split(".")[-1].lower()
        logging.info(f"📤 Received file: {resume.filename}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as temp_file:
            content = await resume.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Extract resume text
        if suffix == "pdf":
            import pdfplumber
            with pdfplumber.open(temp_file_path) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
        elif suffix == "docx":
            import docx
            doc = docx.Document(temp_file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif suffix == "txt":
            with open(temp_file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
        else:
            error_msg = "❌ Unsupported file type. Use .pdf, .docx, or .txt"
            logging.error(error_msg)
            return {"error": error_msg}

        os.remove(temp_file_path)

        # Clean text
        lines = text.splitlines()
        filtered_lines = [line for line in lines if "reference" not in line.lower()]
        cleaned_text = "\n".join(filtered_lines)

        print("📄 Resume preview (first 500 chars):")
        print(cleaned_text[:500])

        job_titles = extract_jobs_from_resume(cleaned_text)

        if not job_titles:
            error_msg = "❌ No job titles could be extracted from the resume."
            logging.error(error_msg)
            return {"error": error_msg}

        logging.info(f"🔍 Extracted job titles: {job_titles}")
        return {"job_titles": job_titles}

    except Exception as e:
        logging.exception("❌ Error in /analyze-resume")
        return {"error": str(e)}


# === STEP 2: Scrape Internshala Jobs ===
import csv
import logging

@app.post("/scrape-jobs")
async def scrape_jobs(request: Request):
    try:
        body = await request.json()
        keyword = body.get("keyword", "").strip()

        if not keyword:
            return {"error": "Missing keyword"}

        fetch_both_internships_and_jobs(keyword)  # ✅ Run scraper

        # ✅ Let file system complete write
        import asyncio
        await asyncio.sleep(1)

        internships = []
        expected_fields = [
            "Title", "Company", "Location", "Stipend",
            "Duration", "Link", "Skills", "Who can apply", "Description"
        ]

        try:
            with open("internshala_internships.csv", newline='', encoding="utf-8") as file:
                # ✅ DO NOT read() before DictReader — it empties the file pointer
                reader = csv.DictReader(file)
                for row in reader:
                    internship_data = {field: row.get(field, "").strip() for field in expected_fields}
                    internships.append(internship_data)
        except Exception as e:
            logging.error(f"⚠️ Error reading internships file: {e}")
            return {"error": "Failed to read internships file."}

        if not internships:
            logging.warning("⚠️ No internships found after scraping.")
            return {"error": f"No internships found for keyword: {keyword}"}

        logging.info(f"✅ Returning {len(internships)} internships.")
        return {"internships": internships}

    except Exception as e:
        logging.error(f"❌ Error: {e}")
        return {"error": "Internal server error"}

# === STEP 3: Auto-apply ===
# === STEP 3: Auto-apply ===
@app.post("/auto-apply")
async def trigger_auto_apply():
    try:
        logging.info("🤖 Starting auto-apply...")
        result = auto_apply()  # returns a dict with status, message, applied

        if result.get("status") == "success" and result.get("applied"):
            logging.info(f"✅ Auto-apply completed. {result['message']}")
            return result  # Return full result with applied details
        else:
            logging.warning("⚠️ Auto-apply did not apply to any internships.")
            return {
                "status": "fail",
                "message": "No applications were submitted. Please try again.",
                "applied": []
            }

    except Exception as e:
        logging.exception("❌ Error in /auto-apply")
        return {"error": str(e), "status": "fail", "applied": []}
