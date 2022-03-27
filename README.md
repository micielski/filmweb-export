<div align="center">
  <h1>🎥 filmweb-export</h1>
  <p>export blazingly fast Filmweb's ratings to a TMDB import-compatible csv file (IMDb v3)</p>
  <img src="https://user-images.githubusercontent.com/73398428/160282968-703dc668-d3b5-4b41-9c12-370ca3995337.png" height="360" width="640">
</div>

# Table of content
- [Features](#features)
- [Installation](#installation)
- [Obtaining cookies](#obtaining-cookies)
- [Usage](#usage)
  - [Example usages](#example-usages)
  - [Docker usage](#docker-usage)
- [Troubleshooting](#troubleshooting)

# Features:

- TMDB.org compatible format (IMDb v3)
- Exports films, serials and a watchlist too
- Multi-threaded
- Supports docker
- Somewhat secure, doesn't permanently store any permanent login credentials on disk

# Installation

  ```
  $ git clone https://github.com/micielski/filmweb-export.git  
  $ cd filmweb-export
  $ pip install -r requirements.txt
  ```
# Obtaining cookies

  Keep in mind, if you have Linux (or Windows, but didn't tested yet) and Geckodriver/Chromium you don't have to authorize with cookies thanks to Selenium support. You can use -i flag instead.
  
  1. Go to a page which requires authentication (i.e. not filmweb main page, but your profile https://filmweb.pl/user/YOUR_USERNAME)
  2. Head to developer tools (press F12 while having focus on a page)
  3. Firefox users, navigate to the Storage tab, while Chromium users; Application tab
  4. Now for both browsers: Cookies -> https://filmweb.pl
  5. You're searching for cookies named \_fwuser_token, \_fwuser_session, JWT. Their values are needed

# Usage
 

  ```
  $ python export.py --help
  usage: export.py [-h] [--username <user>] [--token <token>] [--session <session>]
                   [--jwt <jwt>] [--threads <threads>] [-i] [--force_chrome] [--force_firefox]
  
  Export Filmweb's ratings to a TMDB compatible csv file.
  
  options:
    -h, --help           show this help message and exit
    --username <user>    Filmweb username
    --token <token>      Filmweb token cookie
    --session <session>  Filmweb session cookie
    --jwt <jwt>          Filmweb JSON Web Token
   --threads <threads>  Number of threads to create. Default: 10
    -i                   interactive mode
    --force_chrome       Force Chrome (interactive mode only)
    --force_firefox      Force Firefox (interactive mode only)
  ```

## Example usages

  For people authorizing with cookies  
  You'll be prompted for cookies if you won't specify these with flags.

  ```
  $ python export.py
  ```
  
  People authorizing with username & password using Selenium  
  
  ```
  $ python export.py -i
  ```
  
  Threads  
  It may be useful if your internet connection or computer at this time is poor in resources. In that case try lowering threads count.  
  Please note that the default value is high enough. Going above that, will hurt your exporting performance, and cause some movies to not export!
  
  ```
  $ python export.py --threads 5
  ```
  

## Docker usage
  
  Unfurtunately we don't come with ready image from dockerhub yet. You'll have to build it yourself from Dockerfile in project's root directory  
  After running following command, your export will be waiting in your user's home in the newly created filmweb directory (you'll have to drop its permission though)
  
  ```
    $ docker run -u root -v ~/filmweb:/home/seluser/exports -i <docker image id>
    $ sudo chown $USER ~/filmweb/*
  ```
# Troubleshooting
  
  If your exports seems to not have enough lines [(1 line = 1 movie) + 1], try running the program again, but with different cookies. It could happen that your cookies weren't so fresh during obtaining and so they expired during an export. Also the possibility may be that your internet is not stable and in this case, you would want to lower the threads with --threads flag.  
  If that's not the case, please report an issue. I'll try to respond ASAP!
