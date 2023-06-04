import subprocess, argparse, os

def main():
    global output_path
    global base_path
    global book_title

    parser = argparse.ArgumentParser(description='Takes MP3 files downloaded from Libro.fm and concatenates them into one MP3 file with generated chapters.')
    parser.add_argument('-d','--dir', help='Specify the directory where the MP3 files you wish to concatenate. The directory name should be the same as the title of the audiobook as in the MP3 files.', default='.')

    args = parser.parse_args()
    os.chdir(args.dir)

    cwd = os.getcwd()
    book_title = os.path.basename(cwd)

    output_path = os.path.join(cwd, f"{book_title}.mka")
    base_path = os.path.join(cwd, f"{book_title} - Track")

    cmd = "mkvmerge --ui-language en_US --priority lower --output '{}' --language 0:und".format(output_path)

    cmd = add_tracks(cmd)
    append_sections = append()
    cmd = finishcmd(cmd, append_sections)
    
    # Run the command
    subprocess.run(cmd, shell=True)
    convert_to_mp3()

def add_tracks(cmd: str):
    # Add all tracks to cmd
    for i in range(1, 25):
        track_number = f"{i:03}"
        track_path = f"{base_path} {track_number}.mp3"
        cmd += " '(' '{}' ')' +".format(track_path)

    # Remove trailing '+' from the command
    cmd = cmd[:-2]
    return cmd

def append():
    append_sections = ""
    # Append --append-to sections
    for i in range(1, 24):
        append_section = f"{i}:0:{i-1}:0"
        append_sections += f",{append_section}"

    # Remove first comma
    append_sections = append_sections[1:]
    return append_sections

def finishcmd(cmd: str, append_sections: str):
    # Finish up the command
    cmd += " --chapter-language und --generate-chapters-name-template 'Chapter <NUM:2>' --generate-chapters when-appending --append-to {}".format(append_sections)
    return cmd

def convert_to_mp3():
    mp3_output = os.path.join(os.path.dirname(output_path), f"{book_title}.mp3")
    cmd = f"ffmpeg -i '{output_path}' -c:a copy -c:s copy '{mp3_output}'"
    subprocess.run(cmd, shell=True)

if __name__ == "__main__":
    main()
