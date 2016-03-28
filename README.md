Subjectively useful tools
=========================

fix-video-timestamp (perl):
    Sets the modified date/time to match the original date/time of
  a set of video files. Google Photos does not (at the time of writing)
  use the original date for AVCHD (.MTS files) videos, and instead
  uses the modified date. Running this tool before uploading a video
  will give it the correct timestamp.

  usage: fix-video-timestamp /path/to/files/\*.MTS

git-diff-search (perl):
    Given some source code and a git repository, uses a binary search
  to find the commit with the closest match to the source code (for
  creating a minimized diff to be applied elsewhere).

git-diff-search.py (python):
    Python implementation of git-diff-search, with a different algorithm.
  More reliably finds a "good" minimum, but is less efficient.
