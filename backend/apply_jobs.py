from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import time

def auto_apply():
    driver = webdriver.Chrome()
    with open("temp/jobs.json") as f:
        jobs = json.load(f)
    for job in jobs:
        try:
            driver.get(job["link"])
            # You would add logic to login and apply
            time.sleep(2)
        except Exception as e:
            print(f"Error applying for {job['title']}: {e}")
    driver.quit()
