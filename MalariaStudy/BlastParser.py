#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
date: 02.03.2022
name: BlastParser.py
author: Mirjam Karlsson-Müller

function: Takes a blast output file (from a swissprot database blast) and with the help of
the swissprot database file, a taxonomy database file and a gff parsed fasta file identifies the scaffolds
that contain bird genes. These are then excluded from the filtered genome file.
"""

import sys

blast_out=sys.argv[1] #Blast output file
fna_file=sys.argv[2] #gffParse amino acid sequence file
genome_file=sys.argv[3] #filtered genome fasta file
tax_dat=sys.argv[4] #taxonomy database, in our case: taxonomy.dat
prot_dat=sys.argv[5] #swissprot database, in our case: uniprot_sprot.dat
out_fasta=sys.argv[6] #output fasta file, removed bird scaffolds.

"""Run with:

python BlastParser.py Blast/Ht_blastout.txt gffParse_output/gffParse.faa 
genome_files/Haemoproteus_genome2_filtered.fasta taxonomy.dat uniprot_sprot.dat 
Ht_without_birdscaff.fasta    
"""

#%%
"1. Retrieve top hit for each query, save in dictionary with query ID and hit."

with open(blast_out, 'r') as blast:
    result=True
    blast_dic=dict()
    for line in blast:
        if line.startswith("Query="):
            #new query
            Query=line.strip("\n").split(" ")[1]
            result=False
        if line.startswith(">"):
            if result==False:
                #this is top hit. We extract the accession number, as it is unique.
                hit=line.strip("\n").split("|")[1]
                result=True
                blast_dic[hit]=[Query]

#%%
"2. Check what species the accession number (AC) of the hit corresponds to with uniprot database. "
"Make a new dictionary with query as key and species list as value."

uniprot_dic=dict()
AC_found=False
pot_ac="Null"
oc=[]

with open(prot_dat, 'r') as uniprot:
    for line in uniprot:
        if line.startswith("AC"):
            if AC_found==True:
                if pot_ac in blast_dic:
                    uniprot_dic[blast_dic[pot_ac]]=oc
                    oc=[]
                    AC_found=False
            #new accession number:
            pot_ac=line.strip("\n").split(" ")[1    ]
            AC_found=True    
        
        #Making species list.
        if line.startswith("OC"):
            l=line.strip("\n").split(" ")[1].split(";")
            for i in l:
                oc.append(i.strip(" "))
        
            

#%%
"3. Check if the any of the species in the lists of the previous step is a bird with taxonomy database"

"3a. Make a bird set. yes. its as silly as it sounds."

bird_set=set()
with open(tax_dat, 'r') as taxonomy:
        bird_section=False
        for line in taxonomy:
            #find bird section.
            if line.startswith("BLAST NAME"):
                if "birds" in line:
                    bird_section=True
                elif bird_section==True:
                    break
            elif line.startswith("SCIENTIFIC NAME") and bird_section==True:
                bird_set.add(line.strip("\n").split(":")[1])


"3b. Are our hits birds? "

def is_this_a_bird(l):
    "Checks if any of the names specified in a list are birds."
    for element in l:
        if element in bird_set:
            return(True)
    return(False)
            
            
bird_dic=dict()
for key in uniprot_dic:
    if is_this_a_bird(uniprot_dic[key])==True:
        bird_dic[key]=uniprot_dic(key)


#%%
"4. Read off scaffolds and corresponding query IDs of fasta."

scaffold_dict=dict()
with open(fna_file,'r') as fasta:
    for line in fasta:
        if line.startswith(">"):
            line_list=line.split("\t")
            query_id=line_list[0].strip(">")
            scaffold_info=line_list[2]
            scaffold_number=scaffold_info[9:22]
            if scaffold_number in scaffold_dict: 
                scaffold_dict[scaffold_number].append(query_id)
            else:
                scaffold_dict[scaffold_number]=[query_id]

#%%
"5. Check which scaffolds contain no birds!"
not_a_bird_scaff=dict()
for scaffold in scaffold_dict:
    is_bird=False
    for query in scaffold_dict[scaffold]:
        if query in bird_dic.keys():
            is_bird=True
    if is_bird==False:
        not_a_bird_scaff[scaffold]=scaffold_dict[scaffold]

#%%
"6. Write scaffolds of filtered Ht_file into output file that do not contain birds."

bird_count=0
with open(out_fasta,'w') as output, open(genome_file, 'r') as genome:
    for line in genome:
        if line.startswith(">"):
            line_list=line.split(" ")
            scaffold=line_list[0].strip(">")
            if scaffold in not_a_bird_scaff.keys():
                output.write(line)
                line=next(genome)
                output.write(line)
            else:
                bird_count+=1
    print("The amount of bird scaffolds excluded is: ", bird_count)
