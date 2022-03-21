# Scrape Source Forge 100

## Inspiration
This code is a task done as part of my job application.

### The code here attempts to:
1. Scrape the top 100 software by popularity from Source Forge
2. Find and collect Windows PE files from the downloaded files
3. Rename the files into SHA-1 hash values
4. Zip the files using 7zip GUI (automatically)

## How does this code work in detail.
### Scrape
The code goes to the Source Forge page, specifically windows projects sorted by popularity page one.
The number of project pages to collect can be adjusted. The code will add 25 to any given number.
There are 25 projects listed on a page, the extra page is added because, some projects don't have 
a download link or the extension of the file is unknown.

After all project links are collected, the code loops through each page and retrieves the download
link and file name. The code checks if each file has an acceptable extension - any kind of archive
or a windows portable executable extension. The files that don't fit this or are missing an extension
are skipped. Finally, the links that were gathered are passed to the download function.
If there are more links than requested they will be ignored.

The given links are downloaded - this part takes quite a bit of time, files are downloaded one by one
if the file is more than a few MB it can take up to 10min to download (internet speed efficiency
does not seem to make much of a difference). A progress bar is displayed while downloading.
### Rename_SHA1
After all files are downloaded the code loops through all files in the download folder
when it finds a portable executable it renames the file with SHA-1 hash value and moves
the file to top100 folder. If it finds an archive it attempts to extract files from it
and then searches for portable executables if none are found it prints that to console
otherwise same as with all portable executables. This step again reduces the number of 
files in the final archive.
### Seven_zip
Finally, the code opens up 7z GUI (it attempts to look for it in program files if not
found requests the path to the executable). Selects the top100 directory and then makes
it into an archive and opens up the directory where the archive is.

### Potential errors
- If for whatever reason the code won't be able to connect to selenium driver it will
throw a timeout error
- If connection is lost while downloading the code will either throw an error or get stuck.
Safeguarding for this - when the code is restarted and tries downloading again, it will pass
the links that have been downloaded before (as long as the directory is the same).

## How to run
Run the `main.py` file and all functions will be executed in the order they need to be.

## License
Distributed under the MIT License. See `LICENSE` for more information.