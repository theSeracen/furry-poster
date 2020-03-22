# furry-poster V0.4.2
## `poster.py`
This is a tool for posting a single story to multiple sites. Currently, the following sites are supported:

- FurAffinity
- SoFurry
- Weasyl

Included in this tool are utilities such as thumbnail generation and story file conversion so that formatting displays natively on each website. For more information on this tool, read [Posting Tool](docs/POSTERREADME.md).

## `transfer.py`
This is a tool for transferring a gallery of work from one website to another. This only applies to stories, and the same three sites from above are supported:

- FurAffinity
- SoFurry
- Weasyl

As with the poster tool, the transfer tool contains utilities for story conversion and thumbnail generation. This tool is meant for bulk posting, in essence, using the source gallery as the information collected in `poster.py`. For more information on this tool, read [Transfer Tool](docs/TRANSFERREADME.md).

## Installation
To install, clone the repository and then run `setup.py` with `pip install .` in the working directory. Otherwise, you can also install the required packages listed in the [requirements](requirements.txt).

## Cookies
The program requires authentication for the various websites. This is done via logging in via FireFox and then exporting the cookies in a text file. This text file must be included in the working directory of the program. These files must have specific names to be recognised by the program, namely:

- `cookies.txt'` for a master file and if present, must contain all the cookies for authentication to proceed
- `furaffinitycookies.txt, facookies.txt, fa.txt` for cookies for FurAffinity
- `sofurrycookies.txt, sfcookies.txt, sf.txt` for cookies for SoFurry
- `weasylcookies.txt, wscookies, ws.txt` for cookies for Weasyl

If the `--ignore-errors` flag is not set, a failed authentication on any of the sites will abort the program. An add-in may be necessary to create these files. The following add-on is suitable and creates compatible cookies files, but others exist: [Export Cookies - Firefox Add-On](https://addons.mozilla.org/en-US/firefox/addon/export-cookies-txt/)

