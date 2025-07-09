import streamlit as st
import requests

st.set_page_config(page_title="AI Resume Internship Matcher", layout="centered")
st.title("🎯 AI Resume Internship Matcher")

# === Session State Initialization ===
if "resume_uploaded" not in st.session_state:
    st.session_state.resume_uploaded = False
if "job_titles" not in st.session_state:
    st.session_state.job_titles = []
if "selected_title" not in st.session_state:
    st.session_state.selected_title = ""
if "internships" not in st.session_state:
    st.session_state.internships = []
if "result" not in st.session_state:
    st.session_state.result = {}

# === Step 0: Upload Resume ===
resume_file = st.file_uploader("📄 Upload your resume", type=["pdf", "docx", "txt"])
if resume_file:
    st.session_state.resume_uploaded = True
    st.success(f"📄 Resume `{resume_file.name}` uploaded successfully!")

# === Step 1: Parse Resume ===
if st.session_state.resume_uploaded and st.button("📤 Parse Resume"):
    files = {"resume": resume_file}
    with st.spinner("📄 Extracting job titles from resume..."):
        try:
            res = requests.post("http://localhost:8000/analyze-resume", files=files)
            if res.status_code == 200:
                data = res.json()
                if "error" in data:
                    st.error(f"❌ Error: {data['error']}")
                else:
                    st.session_state.job_titles = data.get("job_titles", [])
                    st.session_state.result = data
                    if st.session_state.job_titles:
                        st.success("✅ Job titles extracted!")
                    else:
                        st.warning("⚠️ No job titles found in resume.")
            else:
                st.error("❌ Failed to analyze resume.")
        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")

# === Step 2: Show Suggested Titles & Select One ===
if st.session_state.job_titles:
    st.subheader("📌 Suggested Job Titles")
    st.session_state.selected_title = st.selectbox("Choose a job title to search internships for:", st.session_state.job_titles)

# === Step 3: Scrape Internshala Internships ===
if st.session_state.selected_title and st.button("🔎 Scrape Internships"):
    with st.spinner(f"Searching internships for '{st.session_state.selected_title}'..."):
        try:
            response = requests.post("http://localhost:8000/scrape-jobs", json={"keyword": st.session_state.selected_title})
            if response.status_code == 200:
                data = response.json()
                if "error" in data:
                    st.error(f"❌ Error: {data['error']}")
                else:
                    st.session_state.internships = data.get("internships", [])
                    if st.session_state.internships:
                        st.success(f"✅ Found {len(st.session_state.internships)} internships")
                    else:
                        st.warning("⚠️ No internships found.")
            else:
                st.error("❌ Server error during scraping.")
        except Exception as e:
            st.error(f"❌ Exception during scraping: {e}")

# === Step 4: Display Internships ===
if st.session_state.internships:
    st.subheader("📄 Top Internship Listings")
    for internship in st.session_state.internships:
        title = internship.get("Title", "No Title")
        company = internship.get("Company", "Unknown")
        link = internship.get("Link", "#")

        st.markdown(f"🔹 **{title}** at *{company}* &nbsp;&nbsp;[🔗 Apply Here]({link})")
# === Step 5: Auto Apply ===
if st.session_state.internships and st.button("🚀 Auto Apply to Top Internship"):
    with st.spinner("Submitting your application automatically..."):
        try:
            response = requests.post("http://localhost:8000/auto-apply")
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    st.success(result.get("message", "Application submitted successfully!"))

                    applied_jobs = result.get("applied", [])
                    if applied_jobs:
                        st.markdown("### ✅ Applied Internships")
                        for job in applied_jobs:
                            st.markdown(f"""
                            **{job['title']}** at **{job['company']}**  
                            🔗 [Link]({job['link']})  
                            🕒 {job['timestamp']}
                            """)
                else:
                    st.error("❌ Auto-apply failed.")
                    st.text(result.get("message", "Unknown error"))
            else:
                st.error("❌ Server error during auto-apply.")
        except Exception as e:
            st.error(f"❌ Exception during auto-apply: {e}")
