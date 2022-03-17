from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import os
import re
import glob
import hashlib
from time import sleep
import urllib.error
import urllib.request
import progressbar
from pyunpack import Archive


pbar = None

DOWNLOAD_DIR = os.path.join((os.environ['USERPROFILE']), r'Desktop\Downloaded-SF\\')


def browser_setup():

    fp = webdriver.FirefoxProfile()

    options = FirefoxOptions()
    #options.headless = True
    caps = DesiredCapabilities().FIREFOX
    caps["marionette"] = True
    driver = webdriver.Firefox(firefox_profile=fp, capabilities=caps, executable_path=GeckoDriverManager().install(),
                               options=options)
    return driver


def show_progress(block_num, block_size, total_size):
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None


def download_url(url, output_dir, filename=None):
    """Download a file and place it in a given directory.
    Args:
        url (str): URL to download file from
        output_dir (str): Directory to place downloaded file in
        filename (str, optional): Name to save the file under. If None, use the basename of the URL
    """
    if not filename:
        filename = url.split('/')[-4]

    output_dir = os.path.expanduser(output_dir)
    fpath = os.path.join(output_dir, filename)
    if not os.path.exists(fpath):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filepath = None
        try:
            print(f'Downloading {url} to {fpath}')
            filepath, _ = urllib.request.urlretrieve(url, fpath, reporthook=show_progress)
        except (urllib.error.URLError, IOError) as e:
            if url[:5] == 'https':
                url = url.replace('https:', 'http:')
                print(f'Failed download. Trying https -> http instead.\n Downloading {url} to {fpath}')
                filepath, _ = urllib.request.urlretrieve(url, fpath, reporthook=show_progress)

        return filepath

    else:
        print(f'{filename} already downloaded')
        return fpath


def get_top_projects(driver, quantity):
    url = fr"https://sourceforge.net/directory/os:windows/?page=1&sort=rating"
    driver.get(url)
    sleep(5)
    cookie = driver.find_element(By.CLASS_NAME, "cmpboxbtn")
    if cookie is not None:
        cookie.click()
    only_links = set()
    while len(only_links) < quantity+10:
        for link in driver.find_elements(By.CLASS_NAME, "see-project"):
            only_links.add(link.get_attribute("href"))
        next_page = driver.find_element(By.CSS_SELECTOR, "[aria-label='Next page']")
        next_page.click()
    only_links = list(only_links)
    return only_links


def clean_text(rgx_list, text):
    new_text = text
    for rgx_match in rgx_list:
        new_text = re.sub(rgx_match, '', new_text)
    return new_text


def get_link_name(links, driver, quantity):
    items = list()
    for link in links:
        link_and_name = list()
        driver.get(link)
        sleep(5)
        try:
            download_button = driver.find_element(By.CLASS_NAME, "button.download")
            link = download_button.get_attribute("href")
            name = download_button.get_attribute("title")
            name = clean_text(['^(Download\s)', '(\sfrom SourceForge\s*.\s\d+.\d+\s[a-zA-Z]+)$'], name)
            link_and_name.append(link)
            link_and_name.append(name)
            items.append(link_and_name)
        except:
            continue
    return items[:quantity]


def scrape():
    sleep(5)
    driver = browser_setup()
    try:
        links = get_top_projects(driver, 25)
        links_names = get_link_name(links, driver, 25)
        for i in links_names:
            download_url(i[0], 'DOWNLOAD_DIR', i[1])
    except Exception as e:
        print(e)
    finally:
        driver.quit()


def get_hash(fpath, out_dir):
    f = open(fpath, 'rb')
    hash_name = hashlib.sha1(f.read()).hexdigest()
    f.close()
    try:
        hashed_name = os.path.join(out_dir, hash_name)
        os.rename(fpath, hashed_name)
    except FileExistsError:
        print('File Already Exists')
    return hash_name


def walkfs(startdir, findfile):
    for root, dirs, files in os.walk(startdir):
        for file in files:
            if file.endswith(findfile):
                found = (os.path.join(root, file))
                return found
    # nothing found, return None instead of a full path for the file
    return None


def rename_sha1(download):
    all_files = list()
    folder = os.path.join(download, 'top100')
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    pe_extensions = (".acm", ".ax", ".cpl", ".dll", ".drv", ".efi", ".exe", ".mui", ".ocx", ".scr", ".sys", ".tsp")
    archive_extensions = ('.zip', '.tar', '.gztar', '.bztar', '.xztar', '.gz', '7z')
    for file in glob.iglob(f'{download}/*'):
        name = os.path.basename(file).split('.')[0]

        if file.endswith(pe_extensions):
            hashed = get_hash(file, folder)
            all_files.append(hashed)

        elif file.endswith(archive_extensions):
            temp_folder = os.path.join(download, name)
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder, exist_ok=True)
            Archive(file).extractall(temp_folder)
            found = walkfs(temp_folder, pe_extensions)
            if found:
                hashed = get_hash(found, folder)
                all_files.append(hashed)
            else:
                print("Portable Executable Not Found")

def seven_zip(files):
    pass


def main():
    # scrape()
    # name = None
    rename_sha1('DOWNLOAD_DIR')
    # files = None
    # seven_zip(files)


if __name__ == "__main__":
    main()
