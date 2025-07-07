# AI Resume Job Matcher

This system takes a resume, extracts suitable job titles using Together AI (LLaMA-3), scrapes jobs from Naukri.com, and can auto-apply using Selenium.

## How to Run

### 1. Install Requirements
```
pip install -r requirements.txt
```

### 2. Start FastAPI
```
uvicorn backend.main:app --reload
```

### 3. Start Streamlit Frontend
```
streamlit run frontend/app.py
```

### 4. (Optional) Auto Apply
```
python backend/apply_jobs.py
```
