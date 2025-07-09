import streamlit as st
import requests
import time

st.set_page_config(page_title="AI Resume Internship Applier", layout="centered")
st.title("🎯 AI Resume Internship Applier")

# === Session State Initialization ===
for key in ["resume_uploaded", "job_titles", "selected_title", "internships", "result"]:
    if key not in st.session_state:
        st.session_state[key] = None if key == "selected_title" else []

# === Step 0: Upload Resume ===
resume_file = st.file_uploader("📄 Upload your resume", type=["pdf", "docx", "txt"])

if resume_file:
    st.success(f"📄 Resume `{resume_file.name}` uploaded successfully!")

    if st.button("🚀 Upload & Auto Apply"):
        total_start = time.time()

        try:
            # === Step 1: Resume Parsing ===
            parse_start = time.time()
            with st.spinner("📄 Parsing resume..."):
                res = requests.post("http://localhost:8000/analyze-resume", files={"resume": resume_file})
            parse_end = time.time()

            if res.status_code != 200:
                st.error("❌ Resume parsing failed.")
                st.stop()

            data = res.json()
            if "error" in data:
                st.error(f"❌ Resume parse error: {data['error']}")
                st.stop()

            st.success(f"✅ Resume parsed in {parse_end - parse_start:.2f} sec")

            st.session_state.job_titles = data.get("job_titles", [])
            st.session_state.result = data

            if not st.session_state.job_titles:
                st.warning("⚠️ No job titles found in resume.")
                st.stop()

            # === Step 2: Auto-select Top Title ===
            st.session_state.selected_title = st.session_state.job_titles[0]
            st.info(f"✅ Top job title selected: **{st.session_state.selected_title}**")

            # === Step 3: Internship Scraping ===
            scrape_start = time.time()
            with st.spinner("🔎 Fetching internships..."):
                response = requests.post(
                    "http://localhost:8000/scrape-jobs",
                    json={"keyword": st.session_state.selected_title}
                )
            scrape_end = time.time()

            if response.status_code != 200:
                st.error("❌ Internship scraping failed.")
                st.stop()

            jobs = response.json()
            st.session_state.internships = jobs.get("internships", [])

            if not st.session_state.internships:
                st.warning("⚠️ No internships found.")
                st.stop()

            st.success(f"🎯 {len(st.session_state.internships)} internships found in {scrape_end - scrape_start:.2f} sec")

            # === Step 4: Auto Apply ===
            apply_start = time.time()
            with st.spinner("🚀 Applying to top internships..."):
                auto_res = requests.post("http://localhost:8000/auto-apply")
            apply_end = time.time()

            if auto_res.status_code != 200:
                st.error("❌ Auto-apply API error.")
                st.stop()

            result = auto_res.json()
            if result.get("status") != "success":
                st.error("❌ Auto-apply failed.")
                st.stop()

            st.success(f"✅ Application submitted in {apply_end - apply_start:.2f} sec")

            applied_jobs = result.get("applied", [])
            if applied_jobs:
                st.markdown("### ✅ Applied Internships")
                for job in applied_jobs:
                    st.markdown(f"""
                    **{job['title']}** at **{job['company']}**  
                    🔗 [Link]({job['link']})  
                    🕒 {job['timestamp']}
                    """)

        except Exception as e:
            st.error(f"❌ Exception occurred: {e}")
            st.stop()

        total_time = time.time() - total_start
        st.info(f"⏱️ Total time taken: {total_time:.2f} seconds")
