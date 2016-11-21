Subjectively useful tools
=========================

**fix-router** *(bash)*:
    While traveling I found some routers not working properly with some
  of my US-based devices, which only use channels 1-11. European routers
  also support channels 12 and 13, and some older Japanese routers support
  channel 14. US devices seem to work best with channels 1, 6, or 11. This
  tool gives you the IP address of the router and scans for the least
  congested network. What you do with that information is up to you.

**fix-video-timestamp** *(perl)*:
    Sets the modified date/time to match the original date/time of
  a set of video files. Google Photos does not (at the time of writing)
  use the original date for AVCHD (.MTS files) videos, and instead
  uses the modified date. Running this tool before uploading a video
  will give it the correct timestamp.
  *example usage*: `fix-video-timestamp /path/to/files/*.MTS`.

**git-diff-search** *(perl)*:
    Given some source code and a git repository, uses a binary search
  to find the commit with the closest match to the source code (for
  creating a minimized diff to be applied elsewhere).

**git-diff-search.py** *(python)*:
    Python implementation of git-diff-search, with a different algorithm.
  More reliably finds a "good" minimum, but is less efficient.

**jsonlint** *(python)*:
    Simple tool to make json more readable. You can use this on a file or
  pipe in some data. *example usage*: `jsonlint data.json`
  or `curl -s1 example.com/data.json | jsonlint`.

**update-certs** *(bash)*:
    Script to dynamically add and update nginx configs and renew letsencrypt
  certifications. Can be run on a daily cron to keep certs up to date.

**verify-transfer** *(node)*:
    After transfering some files (e.g. with rsync) you can use this to
  verify that all the files are the same. It takes a while for large folders
  because it gets the hashes of all files in both directories and
  compares them to make sure they are the same. Works with local or remote
  folders.
  *example usage*: `verify-transfer myusername@example.com:/backup/Photos ~/local/Photos`

Installation
============

For most tools, simply add the folder to your `PATH` environment variable. The
following tools require extra installation steps:

* **verify-transfer**: `npm install`.
