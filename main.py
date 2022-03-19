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
import timeit

pbar = None

DOWNLOAD_DIR = os.path.join((os.environ['USERPROFILE']), r'Desktop\Downloaded-SF\\')


def browser_setup():
    """
    Sets up Selenium to use Firefox and all the needed options for it
    :return: selenium driver to scrape with
    """
    fp = webdriver.FirefoxProfile()

    options = FirefoxOptions()
    options.headless = True
    caps = DesiredCapabilities().FIREFOX
    caps["marionette"] = True
    driver = webdriver.Firefox(firefox_profile=fp, capabilities=caps, executable_path=GeckoDriverManager().install(),
                               options=options)
    return driver


def show_progress(block_num, block_size, total_size):
    """
    Makes the progress bar shown when downloading files. All params are set up by the hook in urllib.request.urlretrieve
     in download_url function.
    :return: None
    """
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


def download_url(url: str, output_dir: str, filename: str = None):
    """
    Download a file and place it in a given directory.
    :param url: (str) URL to download file from
    :param output_dir: (str) Directory to place downloaded file in
    :param filename: (str, optional) Name to save the file under. If None, use the basename of the URL
    :return: Path to the downloaded file
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


def get_top_projects(driver, quantity: int):
    """
    Goes to SourceForge filters to only windows suitable software. Gets the links to the given number of projects +25
    :param driver: Set up selenium driver
    :param quantity: (int) Has to be an increment of 25 (number of projects per page)
    :return: List of links to all scraped projects
    """
    url = fr"https://sourceforge.net/directory/os:windows/?page=1&sort=popular"
    driver.get(url)
    sleep(5)
    cookie = driver.find_element(By.CLASS_NAME, "cmpboxbtn")
    if cookie is not None:
        cookie.click()
    only_links = set()
    while len(only_links) < quantity + 25:
        for link in driver.find_elements(By.CLASS_NAME, "see-project"):
            only_links.add(link.get_attribute("href"))
        next_page = driver.find_element(By.CSS_SELECTOR, "[aria-label='Next page']")
        next_page.click()
    only_links = list(only_links)
    return only_links


def clean_text(rgx_list: list, text: str):
    """
    Cleans up a given string by removing all matching regex patterns
    :param rgx_list: list of regex patterns to remove
    :param text: string that needs to be cleand
    :return: String with all matching regex removed
    """
    new_text = text
    for rgx_match in rgx_list:
        new_text = re.sub(rgx_match, '', new_text)
    return new_text


def get_link_name(driver, links: list, quantity: int):
    """
    Gets the download link and the filename that's downloaded.
    If the filename doesn't have an acceptable extension it is ignored as it can't be used.
    :param links: a list of project links to loop through
    :param driver: Selenium driver
    :param quantity: (int) number of links that need to be returned
    :return: A list of lists. Each smaller list contains project download link and name
    """
    extensions = (
        '.acm', '.ax', '.cpl', '.dll', '.drv', '.efi', '.exe', '.mui', '.ocx', '.scr', '.sys', '.tsp', '.zip', '.tar',
        '.jar', '.gztar', '.bztar', '.xztar', '.gz', '7z')
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
            if name.endswith(extensions):
                link_and_name.append(link)
                link_and_name.append(name)
                items.append(link_and_name)
        except:
            continue
    return items[:quantity]


def get_hash(fpath: str, out_dir: str):
    """
    Renames files with their sha1 hash names.
    :param fpath: path to the file that needs to be renamed
    :param out_dir: directory where the file should be stored
    :return: hash name of the file
    """
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
    """
    Goes through a given directory looking for file with matching extensions.
    :param startdir: (str) Directory where to look for the files
    :param findfile: tuple of accepted extensions
    :return: if file found path to the file else None
    """
    for root, dirs, files in os.walk(startdir):
        for file in files:
            if file.endswith(findfile):
                found = (os.path.join(root, file))
                return found
    # nothing found, return None instead of a full path for the file
    return None


def scrape():
    """
    Sets up the driver, if connection is established will get the links to top projects,
    then uses those links to get the download links and filenames. Finally, loops through the projects and downloads
    them to a specified directory.
    :return: None
    """
    driver = browser_setup()
    try:
        links = get_top_projects(driver, 100)
        links_names = get_link_name(driver, links, 100)
        for i in links_names:
            download_url(i[0], DOWNLOAD_DIR, i[1])
    except Exception as e:
        print(e)
    finally:
        driver.quit()


def rename_sha1(file_dir):
    """
    Goes through all files in a given directory and decides what to do with them based on their extensions
    :param file_dir: directory where to be searched
    :return: Path to folder that contains all files renamed to their hash names
    """
    all_files = list()
    folder = os.path.join(file_dir, 'top100')
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
    pe_extensions = ('.acm', '.ax', '.cpl', '.dll', '.drv', '.efi', '.exe', '.mui', '.ocx', '.scr', '.sys', '.tsp')
    archive_extensions = ('.zip', '.tar', '.gztar', '.bztar', '.xztar', '.gz', '7z', '.jar')
    for file in glob.iglob(f'{file_dir}/*'):
        name = os.path.basename(file).split('.')[0]
        # if file has a portable executable extension it's path is passed to the hash function
        if file.endswith(pe_extensions):
            hashed = get_hash(file, folder)
            all_files.append(hashed)
        # if a file has an archive extension the files are extracted and then searched for a windows PE file
        elif file.endswith(archive_extensions):
            temp_folder = os.path.join(file_dir, name)
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder, exist_ok=True)
            try:
                Archive(file).extractall(temp_folder)
            except Exception as e:
                print(f"Can't extract {file} because:\n{e}")
            found = walkfs(temp_folder, pe_extensions)
            if found:
                hashed = get_hash(found, folder)
                all_files.append(hashed)
            else:
                print(f"Portable Executable Not Found in {temp_folder}")

        else:
            name = os.path.basename(file)
            print(f"{name} is neither an archive nor a portable executable or is missing an extension.")
    return folder

def seven_zip(files):
    pass


def main():
    start = timeit.timeit()
    scrape()
    end = timeit.timeit()
    print(end - start)
    rename_sha1(DOWNLOAD_DIR)
    # files = None
    # seven_zip(files)


if __name__ == "__main__":
    main()
