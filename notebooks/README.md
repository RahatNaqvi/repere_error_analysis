# IPython Notebook

This directory contains various IPython Notebook (also viewable online at http://nbviewer.ipython.org/github/hbredin/repere_error_analysis/tree/master/notebooks/).


## Installation

This will install all the necessary Linux dependencies.

```
$ apt-get install python-pip python-dev build-essential
$ apt-get install gfortran libblas-dev liblapack-dev
$ apt-get install libxml2-dev libxslt-dev
```

This will install all the necessary Python dependencies (and pyannote, in particular) to re-run IPython Notebook locally and write your own analysis with pyannote.

```
$ cd $GIT_REPO/notebooks
$ pip install --process-dependency-links -r requirements.txt 
```

## Usage

Re-run existing IPython Notebook

```
$ cd $GIT_REPO/notebooks
$ ipython notebook
```

Then choose the notebook you want to re-run locally.
Use `Shift + Enter` to run the Python script line after line.

pyannote provides lots of functionality to easily manipulate reference and hypothesis annotations. Why don't you have a look at http://nbviewer.ipython.org/github/pyannote/pyannote-core/blob/master/doc/pyannote.core.annotation.ipynb and http://nbviewer.ipython.org/github/pyannote/pyannote-core/blob/master/doc/index.ipynb)

