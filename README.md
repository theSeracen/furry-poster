# furry-poster V0.1
This is a simple tool for uploading story files to several different furry art sites from a command-line (and only command-line at the moment). `commandmain.py` should be run from the command-line, with a selection of the following flags and options:

## Flags
  - `D,                           directory for story files; must be included`
  - `-i, --ignore-errors          keeps the program running after errors, will abort failed upload attempts`
  - `-F, --furaffinity            upload to FurAffinity`
  - `-S, --sofurry                upload to SoFurry`
  - `-W, --weasyl                 upload to Weasyl`

Flags in the following section are optional. If flags for title, description, or tags are omitted a prompt will be given.
  - `-t, --title                  title for the story`
  - `-d, --description            description for the story; should be given in markdown format`
  - `-k, --tags                   tags or keys to accompany upload; must be comma-separated`
  - `-p, --thumbnail              look for and then upload a thumbnail image`
  - `-c, --convert                find a HTML file and convert it to a text file with BBcode markdown (specifically for FA but works for SoFurry and Weasyl`
  - `-f, --format                 choose from html, markdown for the source file of the story; defaults to markdown`
## Cookies
The program requires authentication for the various websites and this is done via logging into the websites in FireFox and then exporting the cookies in a text file to the working directory of the program. These files must have specific names to be recognised by the program, namely:
  - `cookies.txt'`     - this is the master file and if present, must contain all the cookies for authentication to proceed
  - `furaffinitycookies.txt, facookies.txt, fa.txt`      - cookies for FurAffinity
  - `sofurrycookies.txt, sfcookies.txt, sf.txt`       - cookies for SoFurry
  - `weasylcookies.txt, wscookies, ws.txt`      - cookies for Weasyl
