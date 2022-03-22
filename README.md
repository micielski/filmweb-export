this readme is outdated, please temporarily refer to 
```
$ python export.py -h
```


# :movie_camera: filmweb-export

Export Filmweb's ratings to a TMDB import-compatible csv file.  
Exporting 100 ratings (as of release 4) may take up to ~3 minutes.

## Features:

- themoviedb.org compatible format (IMDb v3)

- Exports both films and serials

## To do:

- [ ] Multi-threading

- [x] Don't require username

- [ ] Docker support

- [ ] Export wantToSee list

## Installation

```
$ git clone https://github.com/xrew11/filmweb-export.git  
$ cd filmweb-export
$ pip install -r requirements.txt
```

## Usage

```
❯ python filmweb.py -h
usage: filmweb.py [-h] [--username <user>] --token <token> --session <session>

Export Filmweb's ratings to a TMDB compatible csv file.

options:
  -h, --help           show this help message and exit
  --username <user>    Filmweb username
  --token <token>      Filmweb token cookie
  --session <session>  Filmweb session cookie
```
