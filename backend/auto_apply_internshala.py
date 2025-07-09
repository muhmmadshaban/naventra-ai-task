def auto_apply(max_jobs=1):
    import os
    import csv
    import time
    import json
    import traceback
    from datetime import datetime
    from dotenv import load_dotenv
    from together import Together
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    load_dotenv()
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
    EMAIL = os.getenv("INTERNSHALA_EMAIL")
    PASSWORD = os.getenv("INTERNSHALA_PASSWORD")

    client = Together(api_key=TOGETHER_API_KEY)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=options)

    MAX_APPLICATIONS = max_jobs
    MAX_FAILURES = 3
    applications_done = 0
    consecutive_failures = 0
    applied_jobs = []

    def log_submission(link, title="Unknown Title", company="Unknown Company"):
        with open("submitted_log.txt", "a", encoding="utf-8") as log_file:
            log_file.write(f"{link.strip().rstrip('/')}\n")

        entry = {
            "title": title,
            "company": company,
            "link": link,
            "timestamp": datetime.now().isoformat()
        }

        file_path = "submitted_details.json"
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except:
                existing = []
        else:
            existing = []

        existing.append(entry)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

        applied_jobs.append(entry)

    def close_popup_modal():
        try:
            close_btn = driver.find_element(By.ID, "close_popup")
            driver.execute_script("arguments[0].click();", close_btn)
            print("✅ Closed popup modal.")
            time.sleep(1)
        except:
            try:
                generic_close = driver.find_elements(By.XPATH, "//button[contains(text(),'×') or contains(text(),'Close')]")
                if generic_close:
                    driver.execute_script("arguments[0].click();", generic_close[0])
                    print("✅ Closed generic modal.")
                    time.sleep(1)
            except:
                print("⚠️ No modal to close.")

    def click_apply_now():
        try:
            apply_btn = driver.find_element(By.CLASS_NAME, "apply_now_btn")
            if "disabled" in apply_btn.get_attribute("class") and "already applied" in apply_btn.text.lower():
                print("⏭️ Already applied (button disabled).")
                return "already_applied"
        except:
            pass

        for attempt in range(3):
            try:
                apply_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "top_easy_apply_button"))
                )
                apply_btn.click()
                print("✅ Clicked top_easy_apply_button.")
                return True
            except:
                try:
                    fallback_btn = driver.find_element(By.XPATH, "//button[contains(text(),'Apply now')]")
                    fallback_btn.click()
                    print("✅ Clicked fallback apply button.")
                    return True
                except:
                    print(f"⚠️ Attempt {attempt + 1}: Apply Now button not clickable.")
                    time.sleep(2)
        return False

    def handle_additional_questions():
        incomplete_block = False

        try:
            availability_radio = driver.find_element(By.ID, "radio1")
            driver.execute_script("arguments[0].click();", availability_radio)
            print("✅ Selected availability: Yes")
        except:
            print("⚠️ Could not select availability radio.")
            incomplete_block = True

        try:
            availability_text = driver.find_element(By.ID, "confirm_availability_textarea")
            availability_text.clear()
            availability_text.send_keys("I am available full-time starting immediately.")
            print("✅ Filled availability description.")
        except:
            print("ℹ️ Availability textarea not found.")

        try:
            question_blocks = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "additional_question"))
            )

            for block in question_blocks:
                handled = False
                try:
                    radios = block.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    for radio in radios:
                        value = radio.get_attribute("value").strip().lower()
                        if value in ["yes", "true", "y"]:
                            driver.execute_script("arguments[0].click();", radio)
                            print(f"✅ Selected radio: {value}")
                            handled = True
                            break

                    textareas = block.find_elements(By.TAG_NAME, "textarea")
                    for ta in textareas:
                        ta.clear()
                        ta.send_keys("https://drive.google.com/sample-portfolio")
                        print("✅ Filled textarea.")
                        handled = True

                    inputs = block.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    for inp in inputs:
                        inp.clear()
                        inp.send_keys("N/A")
                        print("✅ Filled text input.")
                        handled = True

                    if not handled:
                        print("⚠️ Could not handle block completely.")
                        incomplete_block = True
                except:
                    print("⚠️ Error handling question block.")
                    incomplete_block = True
        except:
            print("ℹ️ No additional question blocks found.")

        return not incomplete_block

    def attempt_login(max_attempts=3):
        for attempt in range(max_attempts):
            try:
                WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "modal_email")))
                driver.find_element(By.ID, "modal_email").send_keys(EMAIL)
                driver.find_element(By.ID, "modal_password").send_keys(PASSWORD)
                driver.find_element(By.ID, "modal_login_submit").click()
                print(f"🔐 Login attempt {attempt+1} submitted.")
                time.sleep(5)
                if not driver.find_elements(By.ID, "modal_login_submit"):
                    print("✅ Login successful.")
                    return True
            except Exception as e:
                print(f"⚠️ Login attempt {attempt+1} failed: {e}")
                time.sleep(3)
        print("⛔ Login failed after multiple attempts.")
        return False

    submitted_links = set()
    if os.path.exists("submitted_log.txt"):
        with open("submitted_log.txt", "r", encoding="utf-8") as f:
            submitted_links = set(line.strip().rstrip('/') for line in f)

    with open("internshala_internships.csv", newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        internships = list(reader)

    for job in internships:
        internship_link = job["Link"].strip().rstrip("/")
        internship_title = job.get("Title", "Unknown Title")
        internship_company = job.get("Company", "Unknown Company")

        if internship_link in submitted_links:
            print(f"⏭️ Already applied: {internship_link}")
            continue

        if applications_done >= MAX_APPLICATIONS:
            print(f"\n✅ Reached max limit of {MAX_APPLICATIONS} applications. Exiting.")
            break

        if consecutive_failures >= MAX_FAILURES:
            print(f"\n⛔ Reached {MAX_FAILURES} consecutive failures. Exiting script.")
            break

        print(f"\n🚀 Applying to: {internship_title} at {internship_company}\n🔗 {internship_link}")
        try:
            driver.get(internship_link)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(4)
            close_popup_modal()

            apply_status = click_apply_now()
            if apply_status == "already_applied":
                log_submission(internship_link, internship_title, internship_company)
                continue
            elif not apply_status:
                consecutive_failures += 1
                print(f"❌ Failed to click Apply Now. Consecutive failures: {consecutive_failures}")
                continue
            else:
                consecutive_failures = 0

            try:
                login_link = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[@id='login-link-container']/span"))
                )
                driver.execute_script("arguments[0].click();", login_link)
                print("🪪 Clicked 'Already registered? Login'.")
                time.sleep(2)
            except:
                print("ℹ️ Login link not found or already logged in.")

            if not attempt_login():
                continue

            driver.get(internship_link)
            time.sleep(4)
            close_popup_modal()

            apply_status = click_apply_now()
            if apply_status == "already_applied":
                log_submission(internship_link, internship_title, internship_company)
                continue
            elif not apply_status:
                print(f"❌ Failed to click Apply Now after login. Consecutive failures: {consecutive_failures}")
                continue
            else:
                consecutive_failures = 0

            if not handle_additional_questions():
                print("⚠️ Could not complete additional questions. Skipping application.")
                consecutive_failures += 1
                continue

            try:
                submit_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "submit"))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", submit_btn)
                print("✅ Submit clicked. Waiting for confirmation...")

                time.sleep(5)
                current_url = driver.current_url
                if "matching-preferences" in current_url or "application submitted" in driver.page_source.lower():
                    print(f"🎉 Success: Applied to {internship_title} at {internship_company}.")
                    log_submission(internship_link, internship_title, internship_company)
                    applications_done += 1
                    time.sleep(2)
                    continue
                else:
                    raise Exception("Application submission not confirmed.")

            except Exception as e:
                print("⛔ Submit failed or confirmation not detected.")
                traceback.print_exc()
                consecutive_failures += 1
                continue

        except Exception as general_err:
            print("🚨 Unexpected error:", general_err)
            traceback.print_exc()
            consecutive_failures += 1
            continue

    driver.quit()
    print(f"\n✅ Done applying to {applications_done} internship(s).")
    return {
        "status": "success",
        "message": f"Applied to {applications_done} internship(s).",
        "applied": applied_jobs
    }