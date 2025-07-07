import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_jobs(job_titles):
    jobs = []
    for title in job_titles:
        url = f"https://www.naukri.com/{title.replace(' ', '-')}-jobs"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        for job in soup.select(".jobTuple"):
            try:
                jobs.append({
                    "title": job.select_one(".title").get_text(strip=True),
                    "company": job.select_one(".companyName").get_text(strip=True),
                    "link": job.select_one("a")["href"]
                })
            except:
                continue

    os.makedirs("temp", exist_ok=True)
    with open("temp/jobs.json", "w") as f:
        json.dump(jobs, f, indent=4)

    return jobs
