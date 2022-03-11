# Taxa Finder

*In Progress*

## Necessary Files

<p>Two files are necessary to run Taxa_Finder.py: nodes.dmp and names.dmp. They are part of a collection of files, taxdump, uploaded by ncbi as a part of their taxonomy database.
They can be found in taxdump.tar.gz (or any other zipped format of taxdump) at:<p>

https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/

or downloaded directly over the console with:

wget https://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz 

Make sure to unzip the files regardless of how you download them, and then save them in the same directory as Taxa_finder.py.


## Commands

<p> The script will take a query (or several) and return the lineage from the root of the taxonomic tree to the query (in case of several, for each query). 
  
### Run in command line:
  
```
usage: Taxa_Finder -i INPUT [-s] [-p] -[o] [OUTPUT]
Returns lineage of query based on ncbi`s taxonomy database.

optional arguments:
  -h, --help                                              show this help message and exit
  --input INPUT [INPUT ...], -i INPUT [INPUT ...]         Query name, either single string, or severl strings seperated by space.
  --out [OUT], -o [OUT]                                   Lineage printed in specified output file. Default: Lineage.txt
  --short, -s                                             The lineage returned will only include entries not flagged as hidden by ncbi.
  --print, -p                                             The lineage is printed to console.
  --common, -c                                            Additionally returns the last common taxonomic node of the queries lineage. 
```

### Run in web interface:
Currently only runs on a flask development server. 


## Example of useage
