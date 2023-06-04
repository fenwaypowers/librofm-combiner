import subprocess, argparse, os, json, shutil

num_tracks = 0

def check_dependencies():
    for dependency in ['ffmpeg', 'ffprobe', 'mkvmerge']:
        if shutil.which(dependency) is None:
            print(f"Error: {dependency} is not installed.")
            return False
    return True

def main():
    global output_path
    global base_path
    global book_title
    global num_tracks

    if not check_dependencies():
        return

    parser = argparse.ArgumentParser(description='Takes MP3 files downloaded from Libro.fm and concatenates them into one MP3 file with generated chapters.')
    parser.add_argument('-d','--dir', help='Specify the directory where the MP3 files you wish to concatenate. The directory name should be the same as the title of the audiobook as in the MP3 files.', default='.')

    args = parser.parse_args()
    if not os.path.isdir(args.dir):
        print("Error: the provided directory does not exist.")
        return
    os.chdir(args.dir)

    cwd = os.getcwd()
    book_title = os.path.basename(cwd)

    output_path = os.path.join(cwd, f"{book_title}.mka")
    base_path = os.path.join(cwd, f"{book_title} - Track")

    # Get the number of .mp3 files in the directory
    num_tracks = get_track_count(book_title)
    if num_tracks == 0:
        print("Error: no tracks found.")
        return

    cmd = "mkvmerge --ui-language en_US --priority lower --output '{}' --language 0:und".format(output_path)

    cmd = add_tracks(cmd)
    append_sections = append()
    cmd = finishcmd(cmd, append_sections)
    
    # Run the command
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print("Error: the command failed.")
        return
    extract_cover_image()
    convert_to_mp3()

def get_track_count(book_title: str):
    counter = 0

    for filename in os.listdir():
        if filename.startswith(f"{book_title} - Track") and filename.endswith(".mp3"):
            counter += 1

    return counter

def add_tracks(cmd: str):
    # Add all tracks to cmd
    for i in range(1, num_tracks+1):
        track_number = f"{i:03}"
        track_path = f"{base_path} {track_number}.mp3"
        if os.path.exists(track_path):
            cmd += " '(' '{}' ')' +".format(track_path)

    # Remove trailing '+' from the command
    cmd = cmd[:-2]
    return cmd

def append():
    append_sections = ""
    # Append --append-to sections
    for i in range(1, num_tracks):
        append_section = f"{i}:0:{i-1}:0"
        append_sections += f",{append_section}"

    # Remove first comma
    append_sections = append_sections[1:]
    return append_sections

def finishcmd(cmd: str, append_sections: str):
    # Finish up the command
    cmd += " --chapter-language und --generate-chapters-name-template 'Chapter <NUM:2>' --generate-chapters when-appending --append-to {}".format(append_sections)
    return cmd

def extract_cover_image():
    first_track_path = f"{base_path} 001.mp3"
    if not os.path.exists(first_track_path):
        print("Error: the first track MP3 file does not exist.")
        return

    metadata = subprocess.run(['ffprobe', '-show_streams', '-print_format', 'json', first_track_path], capture_output=True, text=True)
    metadata_json = json.loads(metadata.stdout)

    for stream in metadata_json["streams"]:
        if stream["codec_type"] == "video":
            print("Image metadata found, extracting image...")
            subprocess.run(['ffmpeg', '-y', '-i', first_track_path, '-an', '-codec:v', 'copy', 'cover.jpg'])
            print("Image extracted as cover.jpg")
            return

    print("No image metadata found.")

def prompt_artist_name():
    return input("Please enter the album artist name: ")

def remove_mka_file():
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"Removed {output_path}")
    else:
        print(f"{output_path} not found")

def convert_to_mp3():
    mp3_output = os.path.join(os.path.dirname(output_path), f"{book_title}.mp3")
    cover_path = os.path.join(os.path.dirname(output_path), "cover.jpg")

    artist_name = prompt_artist_name()

    if os.path.exists(cover_path):
        cmd = f"ffmpeg -y -i '{output_path}' -i '{cover_path}' -map 0 -map 1 -c copy -id3v2_version 3 -metadata:s:v title='Album cover' -metadata:s:v comment='Cover (front)' -metadata title='{book_title}' -metadata album='{book_title}' -metadata album_artist='{artist_name}' -metadata artist='{artist_name}' '{mp3_output}'"
    else:
        cmd = f"ffmpeg -y -i '{output_path}' -c:a copy -c:s copy -metadata title='{book_title}' -metadata album='{book_title}' -metadata album_artist='{artist_name}' -metadata artist='{artist_name}' '{mp3_output}'"
    
    subprocess.run(cmd, shell=True)
    
    # Remove the .mka file after .mp3 is created
    remove_mka_file()

if __name__ == "__main__":
    main()
