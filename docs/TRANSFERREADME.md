# `transfer.py`
This is a simple tool for transferring a gallery of stories from one supported site to another. The supported sites are currently:

- FurAffinity
- SoFurry
- Weasyl

For this tool, there are few options and flags. In the course of execution, the program will scan the target user's directory on the source site and load all stories there into memory.Then, it will post each of these to the destination site specified, posting to the account logged in with the cookies file.

If there is a story in the destination account with the same name, then the story will not be posted again. This is to prevent duplicate submissions. The description, tags, and thumbnail from the source website will also be copied over.

## Flags
The following flags are included in the tool:

- `source` -> the source website; choices are:
    - `furaffinity`
    - `sofurry`
    - `weasyl`
- `destination` -> the destination website; same choices as `source`
- `name` -> the username of the person to copy the gallery from

The following flags are optional, and do not need to be included:

- `-d, --delay` -> the number of seconds between story postings; default is 5
- `-t, --thumbnail-behaviour` -> how the tool treats thumbnails; see below for additional details
    - **`new`**
    - `source`
    - `none`
- `-p, --profile` -> profile for thumbnail generation if `-t` flag is set to `new`
- `-f, --force` -> suppresses all prompts and confirmations; **not recommended**
- `--test` -> runs tool without uploading to destination site

## Thumbnail Behaviours
There are three possible options for this flag:

- **`new`**
- `source`
- `none`

The new flag is the default behaviour for the flag when no option is set.

When parsing the target gallery, the thumbnails for each submission can be collected and passed on to the new site i.e. the source submission thumbnail is copied to the destination. This is the behaviour when the flag is set to `source`. However, with this flag, if the source thumbnail does not exist, no thumbnail can be submitted to the destination.

A solution to this, if thumbnails are wanted, is to use the `new` setting. For this, the thumbnail generation utility will be used to create a new thumbnail for the destination submission, regardless of whether one exists for the source. Thus, every submission will have a thumbnail. For more information on the thumbnail generation utility, see [Utilities README](UTILITIESREADME.MD).

### SoFurry Thumbnails
Due to how SoFurry stores and returns thumbnails, every submission has a thumbnail. If none was given at the upload to SoFurry, then this thumbnail is the user icon for the SoFurry account. This will be submitted to the destination site as the transfer tool cannot distinguish between this user icon and a proper thumbnail.

Thus, if there are submission in the source SoFurry gallery that have a user-icon as the thumbnail, it is recommended that the `--thumbnail-behaviour` flag be set to `none` or `new`.

## Website Call Etiquette
Much of this tool's behaviour comes from repeated calls to a website or API and then parsing the result. For this reason, the `--delay` flag was added. Too many requests to a website can overload the connection and cause it to slow done for other users. Additionally, many website have DOS and DDOS protection and may temporarily block IPs that make excessive requests of site resources.

With this in mind, it is recommended to set the delay to a value that is suitable for the task at hand. If there are a large amount of gallery submissions to parse and then post, it is best to set the delay for a higher value. This spaces out the requests and prevents a large amount of connections in a short time.

The delay does not affect the gallery search or parsing, only the time between posts. If the website imposes a 'lockout', then increase the delay further. However, 5 seconds is suitable as a starting point.

Additionally, this is why multiprocessing, threads, or other methods of concurrent program execution will not be implemented. When it comes to website parsing, slow and steady is best.