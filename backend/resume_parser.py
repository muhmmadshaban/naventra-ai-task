from dotenv import load_dotenv
import os
import re
from together import Together

# Load API key from .env file
load_dotenv()
client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

def extract_jobs_from_resume(resume_text: str):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an intelligent resume assistant. "
                    "Analyze the candidate's resume and extract exactly 5 job titles that best match their experience and skills.\n\n"
                    "Rules:\n"
                    "- Only return job titles (not degrees, certifications, awards, or references).\n"
                    "- Output must be numbered: \n"
                    "1. Job Title\n2. Job Title\n...up to 5."
                )
            },
            {
                "role": "user",
                "content": f"Resume:\n{resume_text[:3000]}"
            }
        ]

        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=messages,
            max_tokens=200,
            temperature=0.2,
            top_p=0.9,
            top_k=40,
        )

        # ✅ Correct access pattern for `together` SDK
        output_text = response.choices[0].message.content.strip()
        print("🔁 DeepSeek-V3 Response:\n", output_text)

        # Extract lines starting with numbered bullets
        job_lines = [line.strip() for line in output_text.split("\n") if re.match(r"^\d+\.\s+", line)]

        # Filter and clean titles
        cleaned_titles = []
        for line in job_lines:
            job_title = re.sub(r"^\d+\.\s*", "", line).strip()
            if any(bad in job_title.lower() for bad in [
                "certified", "university", "degree", "award", "reference", "available", "winner", "hackathon", "prize"
            ]):
                continue
            cleaned_titles.append(job_title)

        if not cleaned_titles:
            raise ValueError("❌ No valid job titles extracted.")

        return cleaned_titles[:5]

    except Exception as e:
        print("❌ Exception during job extraction:", e)
        return []
