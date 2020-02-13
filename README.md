# furry-poster V0.31
## `poster.py`
This is a simple tool for uploading story files to several different furry art sites from a command-line (and only command-line at the moment). `poster.py` should be run from the command-line. Currently, only the following furry sites are supported:

- FurAffinity
- SoFurry
- Weasyl

Only the directory of the source files (story and thumbnail) is required from the command-line. However, title, description, and tags are also required; if they are not specified in the command line, a prompt will appear for each missing value. If this prompt is entered without any information, an exception will be thrown and the program will cease. 

It is recommended that each source directory be empty of all other files than the thumbnail and the story file. The program will find and select the first compatible file of each type. This is a `.png` or `.jpeg` file for the thumbnail, and the specified format for the story:

  - `.txt` for the `text` specification
  - `.md` or `.mmd` for the `markdown` specification
  - `.html` for the `html` specification

## Flags
- `D` -> directory for story files; must be included
- `-i, --ignore-errors` -> keeps the program running after errors
- `-F, --furaffinity` -> upload to FurAffinity
- `-S, --sofurry` -> upload to SoFurry
- `-W, --weasyl` -> upload to Weasyl

Flags in the following section are optional. Note that if flags for title, description, or tags are omitted a prompt will be given. Additionally, tags must be written in comma-separated (CSV) format e.g. tag1, tag2, tag3, etc.

- `-t, --title` -> title for the story
- `-d, --description` -> description for the story; should be given in markdown format
- `-k, --tags` -> tags or keys to accompany upload; must be comma-separated
- `-p, --thumbnail` -> boolean flag for whether to look for and then submit a thumbnail. Note that if this flag is set, and a thumbnail cannot be found, an error will occur. Mutually exclusive with `--generate-thumbnail`
- `-g, --generate-thumbnail` -> Causes a thumbnail to be dynamically generated. The default profile is used in thumbnail.config unless specified
- `-f, --format` -> choose from `html`, `markdown`, or `text` for the source file format of the story; defaults to `markdown`
- `-r, --rating` -> choose from `general` and `adult` for the rating of the story; defaults to `adult`
- `-s, --post-script` -> boolean flag to look for a post-script file and add to end of description
- `-m, --messy` -> Flag causes all dynamically-generated files to be saved to the disk

### Post-Script Flag
The post-script must be a text file in the working directory named `post-script.txt`. It may have markdown formatting. The contents of this file is added to the description of every submission with a line break between it and the supplied description. This is to allow repetitive elements, such as Patreon reminders, 'thank-you's, or other footnotes to be added automatically without it having to be re-entered for every description.

### Thumbnail Generation and Story Conversion
The program includes story conversion modules to convert the loaded file to formats that are natively compatible with each site. Additionally, there exists a thumbnail generation utility to create thumbnails if one is not provided, with a number of customisation options. For more details, view the [Utilities README](docs/UTILITIESREADME.md).

### Test and Debug Flags
The following tags are meant to provide additional information, or have testing purposes:

- `--test` -> including this tag will have the program run normally, but no submissions will be made

## Installation
To install, clone the repository and then run `setup.py` with `pip install .` in the working directory. Otherwise, you can also install the required packages listed in the [requirements](requirements.txt).

## Cookies
The program requires authentication for the various websites and this is done via logging in via FireFox and then exporting the cookies in a text file. This text file must be included in the working directory of the program. These files must have specific names to be recognised by the program, namely:

- `cookies.txt'` for a master file and if present, must contain all the cookies for authentication to proceed
- `furaffinitycookies.txt, facookies.txt, fa.txt` for cookies for FurAffinity
- `sofurrycookies.txt, sfcookies.txt, sf.txt` for cookies for SoFurry
- `weasylcookies.txt, wscookies, ws.txt` for cookies for Weasyl

If the `--ignore-errors` flag is not set, a failed authentication on any of the sites will abort the program. An add-in may be necessary to create these files. The following add-on is suitable and creates compatible cookies files, but others exist: [Export Cookies - Firefox Add-On](https://addons.mozilla.org/en-US/firefox/addon/export-cookies-txt/)

## Example
For this example, consider a story that is to be uploaded to all supported sites: FurAffinity, SoFurry, and Weasyl. This adds the flags `-FSW`. A thumbnail will be dynamically generated for the story with the supplied title and tags with `-g`. Additionally, consider that there is a post-script, and that there is a markdown story file: this adds `-sf markdown`. Finally, this is a general story, so `-r general` is added.

If all of the requisite fields for this example story are specified in the command-line, on a Linux machine, then the full command would be similar to the following:

`poster.py -FSW -g -sf markdown -r general -t "Example Title" -d "The example description, with *optional* markdown" -k "Example tag, tag two"`

When this is run, a story named 'Example Title' will be uploaded to FurAffinity, SoFurry, and Weasyl, with a general rating and a generated thumbnail, and a description that includes a postscript.