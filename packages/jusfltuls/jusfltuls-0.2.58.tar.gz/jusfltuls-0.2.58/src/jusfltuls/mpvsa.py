#!/usr/bin/env python3
import click
import sys
import shlex
import subprocess as sp
from console import  fg, bg

import os
import glob

import srt
import re
import datetime as dt
#  like mpv but try to get audio and subtitle based on similarity
#  also creates spectrogram
#
#
#

from jusfltuls.check_new_version import is_there_new_version


def combine(primary_language,  secondary_language, ide, merged_path=None):
    """
    this can create two subtitles in the same srt file - for comparisons
    """
    if merged_path is None:
        print("x... no merging")
        return
    # Read files and convert to list
    primary_path =  primary_language
    secondary_path =  secondary_language
    primary_file = open(primary_path, 'r', errors='ignore')
    primary_text = primary_file.read()
    primary_file.close()
    secondary_file = open(secondary_path, 'r', errors='ignore')
    secondary_text = secondary_file.read()
    secondary_file.close()
    subtitle_generator_primary = srt.parse(primary_text)
    subtitles_primary = list(subtitle_generator_primary)
    subtitle_generator_secondary = srt.parse(secondary_text)
    subtitles_secondary = list(subtitle_generator_secondary)

    # Make primary yellow
    for s in subtitles_primary:
        if ide == 1:
            s.content = '<font color="#ffff54">' + s.content + '</font>' # yell
        elif ide == 2:
            s.content = '<font color="#ff5454">' + s.content + '</font>' # RED
        elif ide == 3:
            s.content = '<font color="#ff54ff">' + s.content + '</font>' # magenta
        else:
            s.content = '<font color="#54ffff">' + s.content + '</font>' # cyan

    # Place secondary on top
    for s in subtitles_secondary:
        s.content = '<font color="#77ff77">' + s.content + '</font>'
        s.content = '{\\an8}' + s.content

    # Merge
    print(f"i... merging to {merged_path}")
    subtitles_merged = subtitles_primary + subtitles_secondary
    subtitles_merged = list(srt.sort_and_reindex(subtitles_merged))

    # Write merged to file
    #merged_path = f"merged_{ide}.srt" # output # "merged.srt"#primary_path.replace(primary_language, 'merged')

    merged_text = srt.compose(subtitles_merged)
    merged_file = open(merged_path, 'w')
    merged_file.write(merged_text)
    merged_file.close()




DEBUG = False
def produce_output_filename(infile, outputname, model_size):
    """
    same in fawhis and mpvsa
    """
    # ================================ OUTPUT ====================
    file_name = "x.srt"
    if DEBUG:
        print(f"> fi {infile}")
        print(f"> di {os.path.dirname(infile)}")
        print(f"> st {os.path.splitext(os.path.dirname(infile))}")
        print(f"> 00 {os.path.splitext(os.path.dirname(infile))[0]}")
        print(f"> --" )
    # --------------------   extract dirname from infile ------------
    dirname = ""
    if os.path.dirname(infile) != "":
        dirname = os.path.splitext(os.path.dirname(infile))[0]
        dirname = f"{dirname}/"
    else:
        dirname = ""
    if DEBUG: print("> dn==", dirname)

    # ----------------------------
    if outputname is not None:
        # ------ cancel my dirname idea if already defined in outputname
        if os.path.dirname(outputname) != "":
            dirname = ""
        if outputname.find(r".srt") > 0:
            file_name = f"{dirname}{outputname}"
        else:
            file_name = f"{dirname}{outputname}.srt"
    else:
        file_name = os.path.splitext(os.path.basename(infile))[0] + f"_{model_size}.srt"
        file_name = f"{dirname}{file_name}"
    return file_name






# ================================================================================
#   constructs the CMD
# --------------------------------------------------------------------------------
def mpvsub( subtitles, audios, video_file):
    opt = ""
    optau = ""
    if subtitles is not None and len(subtitles) > 0:
        for i in subtitles:
            opt = f"{opt} --sub-file={i} "
    if audios is not None and len(audios) > 0:
        for i in audios:
            optau = f"{optau} --audio-file={i} "
    CMD = f"mpv --no-sub-auto {opt} {optau} {video_file}"
    return CMD
    # mpv "${sub_options[@]}" --no-sub-auto  --sid=1 "$video_file"





# ================================================================================
# RUNS
# --------------------------------------------------------------------------------
def runcmd(CMD):
    #CMD = f"mpv {general_filename} --sub-file={another_filename}"
    args = shlex.split(CMD)
    #print(args)
    #print()
    sp.run(args)

def confirm_selection(audio, subtitle):
    print()
    SPC = ""
    print(f"Suggested    Audio:", end="")
    for i in audio:
        print(SPC, i)
        SPC = " " * 20
    if len(audio) == 0:print()
    SPC = ""
    print(f"Suggested Subtitle: ", end="")
    for i in subtitle:
        print(SPC, i)
        SPC = " " * 20
    if len(subtitle) == 0:print()
    print()
    print(f"{fg.orange}Press Enter to confirm, any other key to cancel.{fg.default}")
    choice = input()
    return choice == ''

def get_dirname(infile):
    dirname = ""
    if os.path.dirname(infile) != "":
        dirname = os.path.splitext(os.path.dirname(infile))[0]
        dirname = f"{dirname}/"
    else:
        dirname = ""
    return dirname

# ================================================================================
#   TIME DISTANCE MODE....... works on dtox or original screencast
# --------------------------------------------------------------------------------

def time_distance(video_filename: str, audio_filename: str) -> float:
    # Extract datetime from video filename
    #video_pattern = r"screencast_from_(\d{2})-(\d{2})-(\d{2})_(\d{2})_(\d{2})_(\d{2})"
    video_pattern = r"screencast[_ ]from[_ ](\d{2})-(\d{2})-(\d{2})[_ ](\d{2})[:_](\d{2})[:_](\d{2})"
    v_match = re.search(video_pattern, video_filename)
    if not v_match:
        raise ValueError("Video filename format incorrect")
    dd, mm, yy, HH, MM, SS = v_match.groups()
    video_dt = dt.datetime.strptime(f"{dd}-{mm}-{yy} {HH}:{MM}:{SS}", "%d-%m-%y %H:%M:%S")

    # Extract datetime from audio filename
    audio_pattern = r".*_(\d{8})_(\d{6})"
    a_match = re.search(audio_pattern, audio_filename)
    if not a_match:
        return 99999999
        #raise ValueError("Audio filename format incorrect")
    date_str, time_str = a_match.groups()
    audio_dt = dt.datetime.strptime(date_str + time_str, "%Y%m%d%H%M%S")

    # Return absolute difference in seconds
    return abs((video_dt - audio_dt).total_seconds())



def find_top_matches(video_file, top_n=8, score_cutoff=1, threshold=50.0, time_threshold=60 * 5):
    """
    5 minuts max diff;
    """

    def match_score(name1, name2):
        #print(name1, name2, end=" ")
        score = 0
        for c1, c2 in zip(name1, name2):
            #print(c1, c2, score)
            if c1 == c2:
                score += 1
            else:
                #pass
                break # to end adter 1st failure
        #print(score)
        return score

    def renormalize(scores):
        if not scores:
            return []
        min_score = min(s for s, _ in scores)
        max_score = max(s for s, _ in scores)
        if max_score == min_score:
            return [(100, f) for _, f in scores]
        return [((s - min_score) / (max_score - min_score) * 100, f) for s, f in scores]
    # ---------------------------------------------------------------------------------

    video_base_and_path = os.path.splitext(video_file)[0].lower()
    video_base = os.path.splitext(video_file)[0].lower().split("/")[-1]
    dirname = os.path.dirname(video_file)
    if dirname != "":
        dirname = f"{dirname}/"
        cwd = os.getcwd()
        os.chdir(dirname)
    # I am at video foloder now--------------------

    files = glob.glob("*")
    #print(files)

    #if dirname != "":
        #not yet #files = [os.path.join(dirname, x) for x in files]
        #os.chdir(cwd)

    audio_exts = ('.mp3', '.opus', '.m4a')
    subtitle_ext = '.srt'

    #print(files)
    #files = [x for x in files if len(os.path.splitext(x)[-1]) >= 3] # there is an extension
    files = [x for x in files if (os.path.splitext(x)[-1].lower() in audio_exts) or (os.path.splitext(x)[-1].lower() == subtitle_ext)]
    print(files)

    audio_matches = []
    subtitle_matches = []

    # --------------  I dont have similarity but Screencast stuff
    if video_base.find("screencast_from_") >= 0:
        print(fg.cyan, "i...   MATCHING BASED ON TIME.... limit 5 minutes .....", fg.default)
        for f in files:
            f_lower = f.lower()
            base = os.path.splitext(f_lower)[0]
            #print(base, end=" " )
            a = time_distance(video_base, base)
            #print(a)
            if f_lower.endswith(audio_exts):
                audio_matches.append( (a, f) )
            elif f_lower.endswith(subtitle_ext):
                subtitle_matches.append( (a, f) )

          #subtitle_matches = []
        audio_matches.sort(key=lambda x: x[0])
        subtitle_matches.sort(key=lambda x: x[0])
        audio_matches = [x for x in audio_matches if x[0] < time_threshold]
        subtitle_matches = [x for x in subtitle_matches if x[0] < time_threshold]
        #sys.exit(0)


    else:
        print(fg.green, "i...   MATCHING BASED ON SIMILARITY....  .....", fg.default)
        for f in files:
            f_lower = f.lower()
            base = os.path.splitext(f_lower)[0]
            score = match_score(video_base, base)
            if score >= score_cutoff:
                if f_lower.endswith(audio_exts):
                    audio_matches.append((score, f))
                elif f_lower.endswith(subtitle_ext):
                    subtitle_matches.append((score, f))

        audio_matches = renormalize(audio_matches)
        subtitle_matches = renormalize(subtitle_matches)
        audio_matches = [x for x in audio_matches if x[0] > threshold]
        subtitle_matches = [x for x in subtitle_matches if x[0] > threshold]

        audio_matches.sort(key=lambda x: x[0], reverse=True)
        subtitle_matches.sort(key=lambda x: x[0], reverse=True)


    print("SUB:", subtitle_matches)
    print("AUD:", audio_matches)

    if dirname != "":
        audio_matches = [(x[0], f"{dirname}{x[1]}") for x in audio_matches]
        subtitle_matches = [ (x[0], os.path.join(dirname, x[1])) for x in subtitle_matches]
        os.chdir(cwd)


    top_audio = [f for _, f in audio_matches[:top_n]]
    top_subtitle = [f for _, f in subtitle_matches[:top_n]]

    return top_audio, top_subtitle




@click.command()
@click.argument('video_file', default=None)
@click.option('--spectrum_mp4', '-s', is_flag=True, help="create waterfall spectrum when video_file is audio")
@click.option('--merge', '-m', is_flag=True, help="merge 2 subtitles together")
@click.option('--convert-all-subfolders', '-c', is_flag=True, help='Run embedded bash script')
@click.option('--prepend_silence', '-p', default=0, help='prepend x seconds of silence to opus using ffmppeg')
@click.option('--sox_spectrogram', '-x', is_flag=True, help='use sox and create spectrogram')
def main( video_file, spectrum_mp4, merge, convert_all_subfolders, prepend_silence, sox_spectrogram):
    """
    run mpv with audio+subtit OR join srt subtitles OR create waterfall video OR sox spectrogram
    """

    is_there_new_version(package="jusfltuls", printit=True, printall=True)

    if video_file == "conv":
        print("i... Convering all subfolders TODO")

    if (prepend_silence > 0) and video_file.find("opus") >= len(video_file) - 5:
        base = os.path.splitext(video_file)[0]
        print("i... prepending silence to the ", video_file)
        bash_script = f"""#!/bin/bash
        ffmpeg -y -f lavfi -i anullsrc=r=48000:cl=mono -t {prepend_silence} /tmp/silence_{prepend_silence}.opus
        ffmpeg -i "concat:/tmp/silence_{prepend_silence}.opus|{video_file}" -c copy {base}_silence.opus
        """
        sp.run(bash_script, shell=True, executable='/bin/bash')
        sys.exit(0)

    #
    if sox_spectrogram   and (video_file.find("opus") >= len(video_file) - 5):
        base = os.path.splitext(video_file)[0]
        print("i... creating spectrogram to the ", video_file)
        bash_script = f"""#!/bin/bash
        ffmpeg -y -i {video_file} /tmp/justul_output.wav
        sox /tmp/justul_output.wav -n spectrogram -o {base}.png
        """
        sp.run(bash_script, shell=True, executable='/bin/bash')
        sys.exit(0)


    if convert_all_subfolders:
        bash_script = r"""#!/bin/bash

#for dir in $(ls -d ./*/ 2>/dev/null | sort || echo "./"); do
for dir in $(ls -d ./*/ 2>/dev/null | sort); do :; done; [ -z "$dir" ] && dir="."
    echo "#########################################################################"
    echo "CONVERTING ALL webm,mp3   for opus and srt IN THE FOLDER:  $dir"
    echo "#########################################################################"





    echo -e "\033[33m"  # yellow for webm
    echo "#  VIDEO to INDEXED VIDEO"

  find "$dir" -type f -name "*.webm" | while read -r myfile; do
      echo -e "\033[33m"  # yellow for webm
      output="${myfile%.webm}_converted.webm"
      if [[ "${myfile}" == *_converted* ]]; then
	      echo ... "rekey video ${myfile}"
	  echo "X... Ok... already converted  ${myfile}"
      else
	  if [ ! -f "${output}" ]; then
	      echo ... "rekey video ${myfile}"
	      ffmpeg -hide_banner -i "${myfile}" -c:v libvpx -crf 10 -b:v 1M -keyint_min 1 -g 30 -c:a libvorbis -threads 16 "${output}" </dev/null
	      echo ... "DONE rekey video ${myfile}"
	      sleep 2
	  fi
      fi
  done
  echo -e "\033[0m"




  echo -e "\033[32m"  # green for mp3
   echo "#  MP3 to OPUS "

  find "$dir" -type f \( -name "*.mp3" -o -name "*.m4a" \) | while read -r myfile; do
      echo -e "\033[32m"  # green for mp3
      if [[ "${myfile}" == *m4a* ]]; then
	  output="${myfile%.m4a}_converted.opus"
      fi
      if [[ "${myfile}" == *mp3* ]]; then
	  output="${myfile%.mp3}_converted.opus"
      fi
      if [ ! -f "${output}" ]; then
	  echo ... opusify "${myfile}"
	  ffmpeg  -hide_banner  -i "${myfile}" -c:a libopus -b:a 16k -af "acompressor=threshold=-10dB:ratio=2:attack=50:release=200" -threads 16  "${output}" </dev/null
	  echo ... DONE opusify "${myfile}"
	  sleep 2
      fi
  done
  echo -e "\033[0m"




  echo -e "\033[36m"  # cyan for opus whisper
  echo "#  OPUS to SRT "


find "$dir" -type f -name "*.opus" | while read -r myfile; do
    echo -e "\033[32m"  # green for mp3
    srt_output="${myfile%.opus}.srt"
    if [ ! -f  "${srt_output}" ]; then
        if [[ "${myfile}" == *czech* ]]; then
	    #fawhis
	    echo ... whisper cs "${myfile}"
	    fawhis "${myfile}" -m medium -l cs -o "${srt_output}"
            #uvx --from openai-whisper whisper --device cpu --language cs --model medium --threads 56 --output_format srt  "$file"
            #uvx --from openai-whisper whisper --device cpu --language cs --model medium --threads 56 --output_format srt --output "$srt_output" "$file"
	    echo ... DONE whisper cs "${myfile}"
	    sleep 2
        else
	    echo ... whisper xx "${myfile}"
	    fawhis "$file" -m medium -o "${srt_output}"
            #uvx --from openai-whisper whisper --device cpu --model medium --threads 56 --output_format srt  "$file"
            #uvx --from openai-whisper whisper --device cpu --model medium --threads 56 --output_format srt --output "$srt_output" "$file"
	    echo ... DONE whisper xx "${myfile}"
	    sleep 2
        fi
    fi
done

# ==========================   clean colors;  finish 1st level DO DONE
echo -e "\033[0m"
        echo ... maybe unexpected done error will appear now ....... .........:
done

        """
        sp.run(bash_script, shell=True, executable='/bin/bash')
        sys.exit(0)



    #-------------------------------------------------------
    if video_file is None:
        print("X... give me video file")
        sys.exit(0)



    #fcomment = 6
    #fname = os.path.splitext(video_file)[0]
    # ---------------------- check if sound -----------------------
    sound_exts = {'.mp3', '.opus', '.m4a', '.wav', '.flac', '.aac'}
    exists = os.path.isfile(video_file)
    ext = os.path.splitext(video_file)[1].lower()
    is_sound = ext in sound_exts

    if is_sound:
        print(f"i... {video_file}  is  {fg.orange}SOUND{fg.default}\n")

    if is_sound and spectrum_mp4:
        base, _ = os.path.splitext(video_file)
        mp4_file = base + '.mp4'
        if os.path.isfile(mp4_file):
            print(f"X... file {mp4_file} already exists. ")
            sys.exit(1)
        CMD = f"time ffmpeg  -hide_banner  -i {video_file} -filter_complex showspectrum=mode=combined:scale=sqrt:color=plasma:slide=1:fscale=log:s=300x180:win_func=gauss -y -acodec copy {mp4_file}"
        print(CMD)
        runcmd(CMD)
        sys.exit(0)


    print("i... LOOKING FOR MATCHES....")
    audio, subtitle = find_top_matches(video_file)#best_match(video_file)


    #print("Audio:", audio)
    #print("Subtitle:", subtitle)

    if confirm_selection(audio, subtitle):
        print("Confirmed.")
    else:
        print("Cancelled.")
        sys.exit(0)

    # merging
    if merge:
        subtitle = [x for x in subtitle if x.find("merged") < 0]
        if len(subtitle) > 1:
            for i in range(1, len(subtitle)):
                merged_path = produce_output_filename( subtitle[i], None, model_size=f"merged{i}")
                combine(subtitle[0], subtitle[i], i, merged_path=merged_path)
        print("i... MERGED")
        sys.exit(0)

    cmd = mpvsub(subtitle, audio, video_file)
    print(cmd)
    runcmd(cmd)

# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()
