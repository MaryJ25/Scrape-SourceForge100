from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import sys
import os
from time import sleep


# driver.quit()


def browser_setup():
    download_dir = os.path.join((os.environ['USERPROFILE']), r'Desktop\Downloaded-SF\\')
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    fp = webdriver.FirefoxProfile()
    fp.set_preference("browser.download.folderList", 2)
    fp.set_preference("browser.download.dir", download_dir)
    fp.set_preference("browser.download.manager.showWhenStarting", False)
    fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application" "application/x-7z-compressed"
                                                                "application/vnd.microsoft.portable-executable"
                                                                "application/x-msi" "application/x-dosexec"
                                                                "application/octet-stream" "application/x-gzip")

    options = FirefoxOptions()
    #options.headless = True
    caps = DesiredCapabilities().FIREFOX
    #caps["marionette"] = True
    driver = webdriver.Firefox(firefox_profile=fp, capabilities=caps, executable_path=GeckoDriverManager().install(), options=options)
    return driver


def get_project_links(driver, quantity):
    url = fr"https://sourceforge.net/directory/os:windows/"
    driver.get(url)
    cookie = driver.find_element(By.CLASS_NAME, "cmpboxbtn")
    cookie.click()
    only_links = set()
    while len(only_links) < quantity+10:
        for link in driver.find_elements(By.CLASS_NAME, "see-project"):
            only_links.add(link.get_attribute("href"))
        next_page = driver.find_element(By.CSS_SELECTOR, "[aria-label='Next page']")
        next_page.click()
    only_links = list(only_links)
    return only_links[:quantity]


def download(links, driver):
    for link in links:
        driver.get(link)
        download_file = driver.find_element(By.CLASS_NAME, "download")
        download_file.click()
        sleep(7)
        break


def scrape():
    driver = browser_setup()
    try:
       links = get_project_links(driver, 100)
       download(links, driver)
    except Exception as e:
        print(e)
        driver.quit()
    sleep(60)
    driver.quit()


def rename_sha1(name):
    extensions = ["acm", "ax", "cpl", "dll", "drv", "efi", "exe", "mui", "ocx", "scr", "sys", "tsp"]
    pass


def seven_zip(files):
    pass


def main():
    scrape()
    name = None
    rename_sha1(name)
    files = None
    seven_zip(files)


if __name__ == "__main__":
    main()
