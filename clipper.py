import argparse
import srt
import sys
import os
import re
from termcolor import colored, cprint
from datetime import timedelta
from moviepy.editor import *

ap = argparse.ArgumentParser()
# required
ap.add_argument("inputFile", type=str, help="Input video file path.")
ap.add_argument("srtFile", type=str, help="SRT file path.")
ap.add_argument("dialogue", type=str, help="Dialogue to match in srt file.")
# optional
ap.add_argument("-w", "--window-slide", type=int, help="Time in seconds to move start/end times. Use a negative number to slide backwards.")
ap.add_argument("-p", "--window-pad", type=int, help="Time in seconds to pad the window. Use a negative number to shrink.")
ap.add_argument("-P", "--predict-window", action="store_true", help="Predict the window based on the subtitle content and the position of the matching dialogue.")
ap.add_argument("-A", "--audio-only", action="store_true", help="Export audio only.")
ap.add_argument("-m", "--mode", type=str, default='first', help="How to handle multiple matches - specify 'First','All', or 'Interactive'. Default is 'First'.")
# required
ap.add_argument("outputFile", type=str, help="Output file path. When using 'All' or 'Interactive' modes, place an asterisk in the path to be replaced with the clip number.")
args = ap.parse_args()

srtFile = open(args.srtFile)

subs = srt.parse(srtFile)

def calc_window_prediction(sub, dialogue):
  ls = len(sub.content)
  ld = len(dialogue)

  ss = sub.end.total_seconds() - sub.start.total_seconds()
  i = sub.content.lower().index(dialogue.lower())

  # offsets
  so = (i / ls) * ss
  eo = ((i + ld) / ls) * ss
  
  return sub.start + timedelta(seconds=so), \
         sub.start + timedelta(seconds=(so + (eo - so)))

matches = []

for sub in subs:
  if args.dialogue.lower() in sub.content.lower():
    matches.append(sub)

if len(matches) > 1:
  if args.mode is None or args.mode.lower() == 'first':
    matches = matches[0]
  if args.mode.lower() == 'interactive':
    cprint('Found matches:', 'cyan')
    cprint('---------------------', attrs=['bold'])

    for i in range(len(matches)):
      sub = matches[i]
      di = sub.content.lower().index(args.dialogue.lower())

      line = colored(f'[{i}]', 'cyan') + ' ' \
           + str(sub.start) + colored(' --> ', 'cyan') + str(sub.end) \
           + os.linesep \
           + sub.content[:di] \
           + colored(args.dialogue, 'red') \
           + sub.content[di + len(args.dialogue):]

      print(line)
      cprint('---------------------', attrs=['bold'])

    selected = input('Specify selected matches as a comma separated list: ').split(',')

    matches = [matches[int(i)] for i in selected]

for sub in matches:
  # the default for the window is to match the subtitle display
  window = {'start': sub.start, 'end': sub.end}

  if args.predict_window:
    print('Using predictive window')
    # if raw sub content is not same length as dialogue
    if len(args.dialogue) != len(re.sub(r'\W+', '', sub.content)):
      ps, pe = calc_window_prediction(sub, args.dialogue)
      window = {'start': ps, 'end': pe}
      print(f'Predicted window is: ' + str(window['start']) + ' --> ' + str(window['end']))
  
  if args.window_slide is not None:
    d = timedelta(seconds=args.window_slide)
    window['start'] += d
    window['end'] += d

  if args.window_pad is not None:
    d = timedelta(seconds=args.window_pad)
    window['start'] -= d
    window['end'] += d

  if window['start'].total_seconds() < 0:
    window['start'] = timedelta()
  
  if window['end'].total_seconds() < 0:
    print('Window end was less than 0. Try adjusting.')
    raise

  print(f'Final window is: ' + str(window['start']) + ' --> ' + str(window['end']))
  
  clip = VideoFileClip(f'{args.inputFile}', verbose=True)
  clip = clip.subclip(str(window['start']), str(window['end']))
  
  if args.mode.lower() in ['interactive','all']:
    outputFile = args.outputFile.replace('*', str(matches.index(sub) + 1))
  else:
    outputFile = args.outputFile

  if args.audio_only:
    clip.audio.write_audiofile(f'{outputFile}', codec='pcm_s32le')
  else:
    clip.write_videofile(f'{outputFile}', codec='libx264')

srtFile.close()
