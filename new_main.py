import urllib.error
import urllib.request
import requests
import os
from bs4 import BeautifulSoup
import sys
import progressbar
from time import sleep
pbar = None


def page_error(page):
    if page.status_code != 200:
        print(f"Can't open the page. Status {page.status_code}.")
        sys.exit(1)


def change_page(page):
    try:
        browser = requests.get(f"https://sourceforge.net/directory/{page}")
        page_error(browser)
        return browser
    except:
        print("An error occurred. Check your connection")
        sys.exit(1)


def files_link(links):
    for key, item in enumerate(links):
        links[key] = f'{item}/files/'
    return links


def get_projects(quantity):
    """
    Go to SourceForge, navigate where needed and get the 100 apps
    :return:
    """
    page_number = 1
    browser = change_page(f'?page={page_number}')
    soup = BeautifulSoup(browser.content, "lxml")
    only_links = []
    while len(only_links) < quantity:
        projects = soup.find_all("a", {"class": "see-project"}, href=True)
        for link in projects:
            only_links.append(link['href'])
        page_number += 1
        browser = change_page(f'?page={page_number}')
        soup = BeautifulSoup(browser.content, "lxml")
    return only_links


def get_filenames_and_download_links(links):
    download_name = list()
    for link in links:
        sleep(5)
        try:
            browser = requests.get(f"https://sourceforge.net/{link}")

            page_error(browser)
        except:
            print("An error occurred. Check your connection")
            sys.exit(1)

        soup = BeautifulSoup(browser.content, "lxml")
        # download_button = soup.select("span.sub-label")
        download_button = soup.find('a', {"class": 'download'}, href=True)
        if not download_button:
            download_button = soup.select("span.sub-label")

        print(download_button)


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
    output_dir = os.path.expanduser(output_dir)
    fpath = os.path.join(output_dir, filename)

    if not os.path.exists(fpath):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not filename:
            filename = url.split('/')[-4]

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
        return  fpath


def main():
    links = get_projects(1)
    links = files_link(links)
    get_filenames_and_download_links(links)

main()

#  <a class="button green big-text download with-sub-label extra-wide" href="/projects/mingw/files/latest/download" title="/Installer/mingw-get-setup.exe:  released on 2013-10-04 19:28:56 UTC">


# download_url('https://sourceforge.net/projects/mingw/files/latest/download',
#              'C:/Users/maria/Desktop/SF', 'mingw-get-setup.exe')
