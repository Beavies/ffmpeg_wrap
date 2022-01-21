import glob
import subprocess
import sys

#Global variables
SND_DIR = "snd"

def get_track_number(info: str):
    """
        Return the track number from mkvmerge -i info:
        El ID de la pista 0: video (MPEG-4p10/AVC/h.264)
        El ID de la pista 1: audio (MP3)
    """
    f = info.index(':')
    i = info.rindex(' ', 0, f)
    return info[i+1:f]


def parse_files(lista: list):
    # for each MKV file
    for file in lista:
        # get the track info
        tracks = {'audio': [], 'subtitle': []}
        for linia in subprocess.run(["mkvmerge", "-i", file], capture_output=True, encoding='utf-8').stdout.splitlines():
            if "audio" in linia:
                #get the track number of audio tracks
                tracks['audio'].append(get_track_number(linia))

            if "subtitle" in linia:
                # get the track number of subtitle track
                tracks['subtitle'].append(get_track_number(linia))

        # generate commands
        with open('py-recode.bat', 'a') as f:
            f.write(f'ffmpeg -i "{file}" -c:v libx265 -preset slow -x265-params crf=25 -an "ripped_{file}"\n')
            merge_command = f'mkvmerge -o "FINAL_{file}" "ripped_{file}" '
            track_command = f'mkvextract tracks "{file}" '

            for track in tracks['audio']:
                track_command += f'{track}:{SND_DIR}/{track}.snd '
                merge_command += f'{SND_DIR}/{track}.aac '

            for track in tracks['subtitle']:
                track_command += f'{track}:{SND_DIR}/{track}.sub '
                merge_command += f'{SND_DIR}/{track}.sub '
            
            f.write(track_command + '\n')
            
            for track in tracks['audio']:
                f.write(f'ffmpeg -i {SND_DIR}/{track}.snd -c:a aac -b:a 160k -af "pan=stereo|c0=FL+FC+LFE+BL|c1=FR+FC+LFE+BR" {SND_DIR}/{track}.aac\n')
            
            f.write(merge_command + '\n')
            #f.write(f'del /Q /F /S {SND_DIR} "ripped_{file}" \n\n')
            f.write(f'del /Q /F /S {SND_DIR} \n\n')


## MAIN
# test parameters
if len(sys.argv) <= 1:
    files_to_recode = glob.glob('*.mkv')
else:
    files_to_recode = glob.glob(sys.argv[1])

#print(files_to_recode)
parse_files(files_to_recode)
