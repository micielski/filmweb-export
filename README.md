# :movie_camera: filmweb-export
Export Filmweb's ratings to a TMDB import-compatible csv file.  
Exporting 100 ratings (as of release 4) may take up to ~3 minutes.
  
 ## Installation  
```
git clone https://github.com/xrew11/filmweb-export.git  
cd filmweb-export
pip install -r requirements.txt
```
 ## Usage
 ```
 python filmweb.py -h
  -h, --help        show this help message and exit
  -s, --session    Filmweb Session Cookie
  -u, --username   Filmweb Username Cookie Value
  -t, --token      Filmweb Token Cookie Value
  -f, --firefox    Firefox binary location
  -d, --debugging   Enable debugging
  ```
