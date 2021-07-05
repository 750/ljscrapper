# ljscrapper
LiveJournal parser for article titles, tags, dates by articles' ids.
## Usage
```usage: LJScrapper CLI tool [-h] [--input_file INPUT_FILE] --output_file OUTPUT_FILE [--period PERIOD] blogname

Parse LiveJournal blogs. This tool does not know how to work with blogs that dont have any articles, consider yourself warned.

positional arguments:
  blogname              blogname as in blogname.livejournal.com domain; if the domain is not *.livejournal.com, this argument should be the whole domain
                        name, like varlamov.ru

optional arguments:
  -h, --help            show this help message and exit
  --input_file INPUT_FILE, -i INPUT_FILE
                        path to input file; if not specified, starts from scratch
  --output_file OUTPUT_FILE, -o OUTPUT_FILE
                        path to output file; required
  --period PERIOD, -p PERIOD
                        saves every PERIOD articles, default is 10
```
