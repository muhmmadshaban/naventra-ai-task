# AI Job Auto Apply Bot 🤖

This project automates the process of applying to internships on Internshala using Selenium and logs all successful applications. It uses Together.ai's DeepSeek-V3 model to match resumes with suitable jobs.

## Features

This project automates internship/job applications by integrating AI-based resume parsing with Internshala's job listings.

### 🔁 How It Works (Step-by-Step)

1. 📄 **Resume Parsing**  
   Your resume is parsed and analyzed using `DeepSeek-V3` via Together API to intelligently extract relevant job titles.

2. 🔍 **Job Title Expansion & Matching**  
   The system expands these job titles using semantic similarity and uses them to query Internshala.

3. 🌐 **Internshala Scraping**  
   Jobs and internships matching the relevant titles are scraped from Internshala and stored in `internshala_internships.csv`.

4. ✅ **Smart Auto-Application**  
   The system logs into your Internshala account using `.env` credentials, and applies only to **unapplied and relevant** internships.

5. 📝 **Application Logging**  
   Each successful application is logged in:
   - `submitted_log.txt` → to prevent duplicate applications
   - `submitted_details.json` → includes job title, company, link, timestamp
   - `applied_jobs.csv` → tabular record of applied positions

6. 🧠 **AI-Based Filtering**  
   Uses DeepSeek-V3 to ensure only jobs highly relevant to your skills are retained and targeted.

7. 🌐 **Interactive Streamlit Frontend**  
   - Upload resume
   - View parsed job titles
   - Preview matched internships
   - Click to auto-apply

---

## Highlights

- ✅ Automatically applies to relevant internships from `internshala_internships.csv`
- 🔐 Handles login securely via `.env` credentials
- 🧠 Uses DeepSeek-V3 via Together API for smart job matching
- 📝 Logs submitted internship title, company, link, and timestamp to `submitted_details.json`
- 🌐 Frontend built with Streamlit for user interaction
- 🔁 Re-runs avoided using `submitted_log.txt`
- 📦 Automatically stores all internship and job application details, including job title and company, in CSV files


## Usage

### 1. Set up Environment Variables in `.env`

```
TOGETHER_API_KEY=your_together_api_key
INTERNSHALA_EMAIL=your_email@example.com
INTERNSHALA_PASSWORD=your_password
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Start FastAPI Backend

```bash
uvicorn backend.main:app --reload
```

### 4. Start Streamlit Frontend

```bash
streamlit run frontend/app.py
```

## File Logs
- ✅ `submitted_log.txt` - Stores already applied links to avoid reapplication
- 📝 `submitted_details.json` - Stores detailed metadata of applied internships

## Author

👤 Muhmmad Shaban  
📧 Email: mshaban0121@gmail.com  
🔗 LinkedIn: [linkedin.com/in/muhmmadshaban](https://www.linkedin.com/in/muhmmadshaban)  
🏫 COER University, India

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.