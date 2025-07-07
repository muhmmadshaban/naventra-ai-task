import streamlit as st
import requests

st.set_page_config(page_title="AI Resume Job Matcher", layout="centered")
st.title("🤖 AI Resume Job Matcher")

resume_file = st.file_uploader("📄 Upload your resume", type=["pdf", "docx", "txt"])

if resume_file:
    files = {"resume": resume_file}
    with st.spinner("🔍 Analyzing resume and fetching job matches..."):
        try:
            # Call backend
            response = requests.post("http://localhost:8000/analyze-resume", files=files)

            if response.status_code == 200:
                result = response.json()

                # Handle backend error if present
                if "error" in result:
                    st.error(f"❌ Backend error: {result['error']}")
                    st.stop()

                # ✅ Show Suggested Job Titles
                job_titles = result.get("job_titles", [])
                if job_titles:
                    st.subheader("📌 Suggested Job Titles")
                    for job in job_titles:
                        clean_title = job.split(". ", 1)[-1].strip()  # Remove numbering like "1. "
                        st.markdown(f"- {clean_title}")
                else:
                    st.warning("⚠️ No job titles found.")

                # ✅ Show Job Listings
                jobs = result.get("jobs", [])
                st.subheader("📄 Job Listings")
                if jobs:
                    for job in jobs:
                        if isinstance(job, dict):
                            title = job.get("title", "No Title")
                            company = job.get("company", "Unknown")
                            link = job.get("link", "#")
                            st.write(f"**{title}** at *{company}*")
                            st.write(f"[🔗 Apply Here]({link})")
                        else:
                            st.write(f"🧾 {job}")  # fallback if job is string
                        st.markdown("---")
                else:
                    st.warning("⚠️ No job listings found.")
            else:
                st.error(f"❌ Server error {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"❌ Exception: {e}")
