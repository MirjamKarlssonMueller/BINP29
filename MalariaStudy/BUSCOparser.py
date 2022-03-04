#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
date: 03.03.22
name: BUSCOparser.py
author: Mirjam Karlsson-Müller

executed as:
python BUSCOparser.py 8_full_tsv/ faa_files/ output_fastas/
"""

#%%
"0. Import data"

from pathlib import Path
import sys
import os

tsv_path=Path(sys.argv[1]) #directory containing tsv tables with busco results
tsv_path=tsv_path.glob('*')
faa_path=Path(sys.argv[2]) #directory containing protein sequences for all species
faa_path=faa_path.glob('*')
output_path=Path(sys.argv[3]) #directory for output files.




#%%

"""1. Reading in the tsv tables for all 8 species, making a dictionaryin a dictioanry
 per species containing the BUSCO id, and its corresponding gene ID. For every one but Toxoplasma,
we only include BUSCOs which have COMPLETE, not DUPLICATE. (make value the gene id)
"""
Busco_dict=dict()

for tsv_file in tsv_path:
    with open(tsv_file, 'r') as tsv:
        #Set up outer dictionary with species name
        name=os.path.basename(tsv_file)
        species=name[0:2]
        Busco_dict[species]=dict()
        
        #For all but toxoplasma.
        if species=="Tg":
            for line in tsv:
                #Making sure to exclude the comments in the tsv file
                if line.startswith("#"):
                    continue
                else:
                    info=line.strip("\n").split("\t")
                    status=info[1]
                    #We are only interested in Complete
                    if status=="Complete" or status=="Duplicated":
                        #We add them to the inner dictionary for this species
                        busco=info[0]
                        seq_id=info[2]
                        #It will just be overwritten if its already there, making sure theres only one in the end.
                        Busco_dict[species][busco]=seq_id
        else:
            for line in tsv:
                #Making sure to exclude the comments in the tsv file
                if line.startswith("#"):
                    continue
                else:
                    info=line.strip("\n").split("\t")
                    status=info[1]
                    #We are only interested in Complete
                    if status=="Complete":
                        #We add them to the inner dictionary for this species
                        busco=info[0]
                        seq_id=info[2]
                        Busco_dict[species][busco]=seq_id


#%%
"""2. Remove BUSCOs that are not in all 8 dictionaries."""

last_key=list(Busco_dict.keys())[-1] #Going through the keys of one should suffice
bad_busco=set()

for busco in Busco_dict[last_key]:
    in_all=True
    for species in Busco_dict:
        #If even for one species the busco is not there, flag is false
        if busco not in Busco_dict[species]:
            in_all=False
    #if flag false, the busco is not in all species, thus it can be removed.
    if in_all==False:
        bad_busco.add(busco)

#removing.
for busco in bad_busco:
    for species in Busco_dict:
        if busco in Busco_dict[species]:
            del Busco_dict[species][busco]



#%%
"""3.Make dictionary with outer keys as species, inner keys as gene ids and 
inner values as sequences"""

faa_dict=dict()
for faa_file in faa_path:
    with open(faa_file, 'r') as faa:
        #Find species name
        name=os.path.basename(faa_file)
        species=name[0:2]
        faa_dict[species]=dict()
        
        for line in faa:
            if line.startswith(">"):
                gene_id=line.strip("\n").strip(">").split("\t")[0]
                line=next(faa)
                sequence=line.strip("\n")
                faa_dict[species][gene_id]=sequence


                
#%%

"4. Put it together..."

#list of all buscos
busco_list=list(Busco_dict[last_key].keys())

#iterate through buscos:
for busco in busco_list:
    filename=busco+".fasta"
    outfile=open('{}/{}'.format(output_path, filename), 'w')
    
    for species in Busco_dict:
        gene_id=Busco_dict[species][busco]
        sequence=faa_dict[species][gene_id]
        outfile.write(">{}\n{}\n".format(species, sequence))
    outfile.close()
    
                


