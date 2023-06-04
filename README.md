# Librofm Concatenation Script

This script takes MP3 files downloaded from Libro.fm and concatenates them into one MP3 file with generated chapters. It utilizes various command-line tools such as `ffmpeg`, `ffprobe`, and `mkvmerge`.

## Prerequisites

Make sure the following dependencies are installed:

- ffmpeg
- ffprobe
- mkvmerge

If any of these dependencies are missing, the script will not work correctly.

## Usage

`python main.py [-d|--dir <directory>]`

- `-d|--dir`: Specify the directory where the MP3 files you wish to concatenate are located. The directory name should be the same as the title of the audiobook as in the MP3 files. (default: current directory)

## Example

`python main.py -d /path/to/audiobook`

## Workflow

1. Check dependencies: Ensures that the required dependencies are installed.
2. Parse command-line arguments: The script accepts an optional directory argument to specify the location of the MP3 files.
3. Change to the specified directory: Sets the working directory to the provided directory.
4. Get book title and output paths: Determines the book title based on the directory name and sets the output path for the concatenated audio file.
5. Count tracks: Retrieves the number of MP3 tracks in the directory.
6. Construct the initial command: Creates the initial command for `mkvmerge` to merge the tracks.
7. Add tracks to the command: Appends all tracks to the command.
8. Append sections: Generates section information for chapter creation.
9. Finalize the command: Adds chapter generation options and append sections to the command.
10. Execute the command: Runs the `mkvmerge` command to concatenate the tracks.
11. Extract cover image: Extracts the cover image from the first track if present.
12. Prompt for artist name: Asks the user to enter the album artist name.
13. Convert to MP3: Converts the concatenated audio file to MP3 format, adding metadata and cover image if available.
14. Clean up: Removes the intermediate `.mka` file.

Note: The script assumes that the MP3 files in the directory follow the naming convention `"<book_title> - Track 001.mp3"`, `"Track 002.mp3"`, and so on.
