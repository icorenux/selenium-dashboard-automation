import os
import shutil
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# configuration 
mac_username = ""
dashboard_list_url = "https://app.datadoghq.com/dashboard/lists?p=1"

original_profile = f"/Users/{mac_username}/Library/Application Support/Google/Chrome/Default"
duplicate_profile = f"/Users/{mac_username}/Library/Application Support/Google/Chrome_Selenium"

# copy chrome profile 
if not os.path.exists(duplicate_profile):
    print("Copying chrome profile for selenium use")
    shutil.copytree(original_profile, duplicate_profile)
else:
    print("Using existing chrome_selenium profile")

# setup selenium 
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={duplicate_profile}")
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)

try:
    driver = webdriver.Chrome(options=chrome_options)
except WebDriverException as e:
    print("Failed to start chrome webdriver")
    print(e)
    exit(1)

def wait_and_click(by, value, timeout=20):
    WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, value))).click()

try:
    print("Navigating to dashboard list")
    driver.get(dashboard_list_url)
    time.sleep(5)

    # get all dasahboard 
    dashboard_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/dashboard/')]")
    visited = set()
    dashboard_urls = []
    for link in dashboard_links:
        href = link.get_attribute("href")
        if href and href not in visited:
            dashboard_urls.append(href)
            visited.add(href)

    print(f"Found {len(dashboard_urls)} dashboards")

    # open CSV file to store dashboard + teams
    with open("dashboard-list.txt", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)

        for url in dashboard_urls:
            print(f"\nChecking: {url}")
            driver.get(url)
            time.sleep(3)

            try:
                wait_and_click(By.XPATH, "//button[contains(., 'Configure')]")
                print("Clicked Configure")

                wait_and_click(By.XPATH, "//span[contains(., 'Permissions')]")
                print("Opened Permissions")

                time.sleep(3)

                team_elements = driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'druids_layout_grid')]//div[contains(@class, 'druids_layout_overflower__original')]"
                )

                for team in team_elements:
                    name = team.text.strip()
                    if name:
                        print(f"- {name}")
                        writer.writerow([url, name])

            except Exception as inner_e:
                print(f"Error while processing dashboard: {inner_e}")

except Exception as e:
    print("Fatal Error:", e)

finally:
    driver.quit()
