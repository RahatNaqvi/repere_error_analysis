
## Installation

This will install all the necessary Linux dependencies.

```
$ apt-get install python-pip python-dev build-essential
$ apt-get install gfortran libblas-dev liblapack-dev
$ apt-get install libxml2-dev libxslt-dev
```

This will install all the necessary Python dependencies (and pyannote, in particular) to re-run IPython Notebook locally and write your own analysis with pyannote.

```
$ pip install -U --process-dependency-links \
    pyannote.parser \
    pyannote.metrics \
    docopt
```

## Usage

```
$ python stats_spkshow.py --help
```
