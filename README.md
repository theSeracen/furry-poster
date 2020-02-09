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
  - `-d, --description            description for the story`
  - `-k, --tags                   tags or keys to accompany upload`
  - `-p, --thumbnail              look for and then upload thumbnail image`
  - `-c, --convert                find a HTML file and convert it to a text file with BBcode markdown (specifically for FA but works for SoFurry and Weasyl`
