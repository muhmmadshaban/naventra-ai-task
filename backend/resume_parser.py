from dotenv import load_dotenv
import together
import os

load_dotenv()  # Load TOGETHER_API_KEY from .env
def extract_jobs_from_resume(resume_text: str):
    try:
        from together import Complete
        prompt = f"""You are an expert career assistant.
Based on the resume content below, analyze the skills and experience, and then suggest exactly 5 suitable job titles. 
Only return the job titles as a numbered list like:

1. Job Title 1
2. Job Title 2
3. Job Title 3
4. Job Title 4
5. Job Title 5

Resume:
{resume_text[:3000]}
"""

        response = Complete.create(
            model="meta-llama/Llama-3-70b-chat-hf",
            prompt=prompt,
            max_tokens=200,
            temperature=0.7,
            top_k=50,
            top_p=0.9,
        )

        print("🔁 Together API full response:")
        print(response)

        if not response or "choices" not in response:
            raise ValueError(f"❌ Unexpected Together API response: {response}")

        job_text = response["choices"][0]["text"]

        # Extract lines that look like numbered job titles
        job_lines = [line.strip() for line in job_text.split('\n') if line.strip().startswith(("1.", "2.", "3.", "4.", "5."))]

        # Fallback: all non-empty lines
        if not job_lines:
            job_lines = [line.strip() for line in job_text.split('\n') if line.strip()]

        return job_lines[:5]

    except Exception as e:
        print("❌ Together API Exception:", e)
        raise e
