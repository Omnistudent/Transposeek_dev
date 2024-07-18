The readme for Transposeek

Installation

Install git
https://github.com/git-guides/install-git

Using a command line window, go to an empty folder and type
git clone https://github.com/Omnistudent/transposeek2

Running the program

go to the folder transposeek2 in the command line window,
cd transposeek2

In the cloned folder, type
python manage.py runserver

Go to http://127.0.0.1:8000/ in a web browser

A default blastx and IS protein database is included with the project file, in the "static" folder.
The static folder also contains the folder "genomes", which is the default location for the genome files. The folder contains one sample file.
The format for the genome files should be genbank and it should contain a continious nucletide sequence. Contigs should be joined into a continuous file with zero spacing nucleotides.

By default, results are written to 
static/analysed_gb_files    - genbank files with insertion sequences marked out.
static/is_list_csv          - tab separated spreadsheet with information about ISs on genome

Usage

On the tab "Manage genomes", add genome files from the current folder (middle window) to the database of investigated genomes (left window).
Click the "Home" tab.
For each genome, click the buttons from left to right. Wait for each process to finish (the web window stops loading).
Processes that have been run and have a recognizable result file are colored green, while processes that are marked red have not been run yet.

Requirements:
python
biopython
matplotlib

admin to database is theo/1234
the adress to administrate the database is http://127.0.0.1:8000/admin/

The program is under development, much unused code remains to be deleted.


