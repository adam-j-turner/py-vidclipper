## py-vidclipper

Python script to clip video (and audio from video) by matching dialogue from a subtitle (SRT) file. Supports Python 3 only.


### Usage
```
usage: clipper.py [-h] [-w WINDOW_SLIDE] [-p WINDOW_PAD] [-P] [-A] [-C]
                  [-m MODE]
                  inputFile srtFile pattern outputFile

positional arguments:
  inputFile             Input video file path.
  srtFile               SRT file path.
  pattern               Pattern to match in srt file. Can be regex.
  outputFile            Output file path. When using 'All' or 'Interactive'
                        modes, place an asterisk in the path to be replaced
                        with the clip number.

optional arguments:
  -h, --help            show this help message and exit
  -w WINDOW_SLIDE, --window-slide WINDOW_SLIDE
                        Time in seconds to move start/end times. Use a
                        negative number to slide backwards.
  -p WINDOW_PAD, --window-pad WINDOW_PAD
                        Time in seconds to pad the window. Use a negative
                        number to shrink.
  -P, --predict-window  Predict the window based on the subtitle content and
                        the position of the matching pattern.
  -A, --audio-only      Export audio only.
  -C, --case-sensitive  Use case sensitive matching. Defaults to case
                        insensitive.
  -m MODE, --mode MODE  How to handle multiple matches - specify
                        'First','All', or 'Interactive'. Default is 'First'.
```

### Example
`python3 clipper.py /movies/spiderman-2.mp4 /movies/spiderman-2.srt 'Pizza time' ~/pizza.mp4`
