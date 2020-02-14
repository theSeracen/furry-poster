# Utilities
## File Conversion
The program will automatically convert the selected file in memory to a format that is compatible with each website. This is markdown for Weasyl, and BBcode for FurAffinity and SoFurry. This means that the source directory doesn't need to be cluttered with unnecessary files. However, if these files are desired, then the `--messy` flag can be used and any generated files will be saved to the specified directory as they're converted.

Note that the HTML conversion is particularly sensitive. Complex HTML files may not be parsed correctly due to the wide variation of possible tags and configurations. It is best to set the source file as a `.txt` file with BBcode or markdown formatting, or use markdown natively in `.mmd` or `.md` files. The only HTML files that can be said to work correctly with 100% surety are those produced by the Scrivener writing program with particular settings. This option is only included for legacy reasons and may be removed in future version.

As such, **markdown source files are recommended**. These can be made in any text editor, using markdown syntax and saved with the `.md` or `.mmd` extension. See [Markdown Syntax](https://daringfireball.net/projects/markdown/syntax) for the allowable formatting. However, BBcode will also convert without issue, though it is more difficult to write and care must be taken with the tags.

## Thumbnail Generation
There is a thumbnail generation utility included in the program. A `thumgnail.config` file contains all of the configurations options for this generation. Unless the `--messy` flag is included, the generated thumbnail is kept solely in memory and is not saved to a file. The options contained in the config file are explained below.

- `width` -> the width of the thumbnail
- `height` -> the height of the thumbnail
- `backcolour` -> background colour as three comma-separated RGB values
- `titleStartCoords` -> two X,Y values for where title should begin
- `titleColour` -> title text colour as three comma-separated RGB values
- `tagColour` -> same as `titleColour` but for the tags
- `tagBottomBorder` -> minimum pixels beneath the tags
- `titleTagSepDist` -> number of pixels between the title text and the top tag
- `maxTags` -> maximum number of tags to display on the thumbnail
- `minTitleSize` -> the minimum size for the title to be
- `maxTitleSize` - > the maximum allowable size for a title to reach

Note that for each of the supplied value, the format **must be the same as given**. For example, if specifying a new background colour, it must be specified as three integer values separated with a comma and a space e.g. `0, 0, 0`. If spaces are added or removed, or commas are missing, exceptions shall occur and fatally disrupt the execution of the program to give the opportunity to correct the misconfiguration.

### New Profiles
New profiles to the thumbnail configuration file can be added via copying and pasting the existing section, and then changing the header value i.e `[default] -> [new profile]`. The name of this new profile can then be passed to the program via the `--generate-thumbnail` flag to create the thumbnail with the desired characteristics.

It is **highly recommended** not to delete the default profile. If the program is ever run without the flag set, then a fatal error will occur. 