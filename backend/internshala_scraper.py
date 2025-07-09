import csv
import time
import re
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from together import Together

# === Helpers ===
def get_element_text_safe(parent, xpath):
    try:
        return parent.find_element(By.XPATH, xpath).text.strip()
    except NoSuchElementException:
        return None

def get_element_attr_safe(parent, xpath, attr):
    try:
        return parent.find_element(By.XPATH, xpath).get_attribute(attr)
    except NoSuchElementException:
        return None

def expand_keywords_with_together(api_key: str, base_keyword: str):
    import re
    from together import Together

    # Clean the input keyword: remove special characters
    cleaned_keyword = re.sub(r"[^a-zA-Z0-9 ]", "", base_keyword).strip()
    print(f"🔍 Cleaned base keyword: {cleaned_keyword}")

    prompt = (
        f"Suggest 5 related job titles for internships or full-time roles similar to: '{cleaned_keyword}'. "
        f"Return a comma-separated list only. No explanations."
    )

    try:
        client = Together(api_key=api_key)

        response = client.chat.completions.create(
            model="meta-llama/Llama-3-70b-chat-hf",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            stop=["\n"]
        )

        raw_output = response.choices[0].message.content.strip()
        raw_output = re.sub(r"(?i)^.*?:", "", raw_output)  # Remove “Here are…” if present
        keywords = re.split(r",|\n|;", raw_output)
        cleaned_keywords = [kw.strip().lower() for kw in keywords if kw.strip()]

        if not cleaned_keywords:
            print("⚠️ No expanded keywords returned by API. Falling back to cleaned base keyword.")
            return [cleaned_keyword.lower()]

        expanded = list(set([cleaned_keyword.lower()] + cleaned_keywords))
        print(f"🔍 Expanded keywords: {expanded}")
        return expanded

    except Exception as e:
        print(f"⚠️ Together API error: {e}")
        return [cleaned_keyword.lower()]

# === Main Crawl Function ===
def crawl_internshala_by_type(keyword: str, limit: int, type_: str):
    print(f"\n🔎 Crawling '{type_}' for keyword: {keyword}")
    url_keyword = keyword.strip().replace(" ", "-")
    url = f"https://internshala.com/{type_}s/keywords-{url_keyword}/"

    # Selenium Setup
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    load_dotenv()
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    expanded_keywords = expand_keywords_with_together(TOGETHER_API_KEY, keyword)

    jobs = []
    try:
        driver.get(url)
        time.sleep(3)

        # Close popup
        try:
            close_btn = driver.find_element(By.ID, "close_popup")
            driver.execute_script("arguments[0].click();", close_btn)
        except:
            pass

        cards = driver.find_elements(By.CLASS_NAME, "individual_internship")
        i = 0
        count = 0

        while i < len(cards) and count < limit:
            try:
                cards = driver.find_elements(By.CLASS_NAME, "individual_internship")
                card = cards[i]

                title = get_element_text_safe(card, ".//h3/a") or get_element_text_safe(card, ".//div[contains(@class,'internship_title')]//a")
                if not title:
                    i += 1
                    continue

                company = get_element_text_safe(card, ".//div[contains(@class,'company_name')]/div/p") or "N/A"
                location = get_element_text_safe(card, ".//div[@class='location_link']") or "N/A"
                stipend = get_element_text_safe(card, ".//span[@class='stipend']") or "N/A"
                duration = get_element_text_safe(card, ".//i[@class='ic-16-calendar']/following-sibling::span") or "N/A"
                link = get_element_attr_safe(card, ".//a", "href")
                if link and not link.startswith("http"):
                    link = f"https://internshala.com{link}"

                # Open in new tab to extract more details
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                time.sleep(2)

                description = get_element_text_safe(driver, "//div[@class='text-container']") or "N/A"
                skills = get_element_text_safe(driver, "//div[contains(text(),'Skill(s) required')]/following-sibling::div") or "N/A"
                who_can_apply = get_element_text_safe(driver, "//div[contains(text(),'Who can apply')]/following-sibling::div") or "N/A"

                driver.close()
                driver.switch_to.window(driver.window_handles[0])

                # Clean and check title + description
               # Clean and check title + description
               
                def clean_text(text):
                    return re.sub(r'[^a-zA-Z0-9 ]', ' ', text).lower().strip()
                
                def tokenize(text):
                    return set(clean_text(text).split())
                
                def is_relevant_job(title, description, expanded_keywords):
                    full_text_tokens = tokenize(f"{title or ''} {description or ''}")
                
                    for keyword in expanded_keywords:
                        keyword_tokens = tokenize(keyword)
                        if keyword_tokens & full_text_tokens:  # set intersection
                            return True
                    return False
                
                # Usage example inside loop
                if not is_relevant_job(title, description, expanded_keywords):
                    print(f"❌ Skipped card {i+1}: Not relevant to '{keyword}' or similar terms")
                    i += 1
                    continue
                
                

                jobs.append({
                    "Title": title,
                    "Company": company,
                    "Location": location,
                    "Stipend": stipend,
                    "Duration": duration,
                    "Link": link,
                    "Skills": skills,
                    "Who can apply": who_can_apply,
                    "Description": description
                })
                count += 1
                print(f"{count}. ✅ {title} at {company}")
            except StaleElementReferenceException:
                print(f"⚠️ Skipped card {i} due to stale reference.")
            except Exception as e:
                print(f"⚠️ Error at card {i}: {e}")
            i += 1
    finally:
        driver.quit()

    if jobs:
        file_name = f"internshala_{type_}s.csv"
        with open(file_name, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
            writer.writeheader()
            writer.writerows(jobs)
        print(f"\n📦 Saved {len(jobs)} to {file_name}")
    else:
        print(f"\n❌ No {type_}s saved.")

# === Final Master Function ===
def fetch_both_internships_and_jobs(keyword: str):
    crawl_internshala_by_type(keyword=keyword, limit=5, type_="internship")
    crawl_internshala_by_type(keyword=keyword, limit=5, type_="job")
