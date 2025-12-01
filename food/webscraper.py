# IMPORTS

# os
import os

# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# time
from time import sleep


# SETUP

# get local directory
dir = os.path.dirname(os.path.abspath(__file__))

# set firefox instance download folder to local directory
firefox_options = Options()
firefox_options.set_preference("browser.download.folderList", 2)
firefox_options.set_preference("browser.download.dir", dir)

# initialise new firefox instance
driver = webdriver.Firefox(options=firefox_options)

# query sg food id tool
driver.get("https://pphtpc.hpb.gov.sg/web/sgfoodid/tools/food-search?searchText=a")


# QUERY PAGES HANDLER

# wait for page links to load
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'page-link')]"))
)

# loop through page links to find page max
page_max = 1
for page_link in driver.find_elements(By.XPATH, "//a[contains(@class, 'page-link')]"):

    # get id of page link
    id = page_link.get_attribute("id")

    # check if id exists and is numerical
    if id and id.isdigit():

        # check for new page max
        page_max = max(page_max, int(id))

# loop until max page inclusive
for page in range(1, page_max + 1):

    # query sg food id tool with page number
    driver.get(f"https://pphtpc.hpb.gov.sg/web/sgfoodid/tools/food-search?searchText=a&pageNumber={page}")


    # FOOD RECORDS HANDLER

    # wait for records to load
    records = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//tbody"))
    )

    # get list of record names from records table
    record_names = [record.find_element(By.XPATH, ".//div[contains(@class, 'text-primary')]").text for record in records.find_elements(By.XPATH, ".//tr")]

    # loop through each record
    for record_name in record_names:

        # find and click table row with record name to enter record details page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), \"{record_name}\")]"))
        ).click()

        # find and click button to download record as csv
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Export as CSV')]"))
        ).click()

        # go back to records list page
        driver.back()

        # to avoid getting rate-limited
        sleep(1)