from variables import FOLDER
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.common.exceptions import NoSuchElementException
import sys
import os
from time import sleep

# driver.quit()


def browser_setup():
    path = os.path.join(os.environ['USERPROFILE'], FOLDER, r'geckodriver-v0.30.0-win64\geckodriver.exe')
    print(path)
    options = FirefoxOptions()
    # options.headless = True
    # caps = DesiredCapabilities().FIREFOX
    # caps["marionette"] = True
    driver = webdriver.Firefox(executable_path=path, options=options)
    return driver


def open_page(driver, url):
    main_page = "https://sourceforge.net/"
    # adjusts the link to go to the correct page
    browser = driver.get(main_page + url)
    return browser


def get_project_links(quantity):
    pass


def download(links):
    pass


def scrape():
    driver = browser_setup()
    open_page(driver, r"directory/os:windows/?page=2")
    sleep(5)
    driver.quit()
    # links = get_project_links(100)
    # download(links)


def rename_sha1(name):
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