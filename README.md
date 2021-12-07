# :movie_camera: filmweb-export
Export Filmweb's ratings to a TMDB import-compatible csv file.  
Please note, that exporting 100 ratings (as of release 3) may take up to ~15 minutes.
  
 ## Installation  
```
pip install bs4 selenium argparse
git clone https://github.com/xrew11/filmweb-export.git  
cd filmweb-export
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
