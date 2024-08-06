# Transposeek

## Requirements:
python 3.10 (may work on other)

biopython

matplotlib

beautifulsoup4

requests


## Installation

Install git from

https://github.com/git-guides/install-git

Using a command line window, go to an empty folder and type
```
pip install django BioPython matplotlib bs4 requests
```

and then
```
git clone https://github.com/Omnistudent/transposeek2
```



## Running the program

go to the folder transposeek2 in the command line window,
```
cd transposeek2
```

In the cloned folder, type
```
python manage.py runserver
```

Go to http://127.0.0.1:8000/ in a web browser

A default blastx and IS protein database is included with the project file, in the "static" folder.
The static folder also contains the folder "genomes", which is the default location for the genome files. The folder contains one sample file.
The format for the genome files should be genbank. Multiple contigs will be joined into a continuous file with zero spacing nucleotides.

By default, results are written to the folder static/final_results, located in the program folder.

## Usage

On the tab "Manage genomes", add genome files from the current folder (middle window) to the database of investigated genomes (left window).
Click the "Search" tab.
For each genome, click the blast button. Wait for the process to finish (the web window stops loading). This takes 2-15 minutes.
Processes that have been run and have a recognizable result file are colored green, while processes that are marked red have not been run yet.

## Notes
The admin account to the database is theo/1234.
the adress to administrate the database is http://127.0.0.1:8000/admin/

The program is under development.
