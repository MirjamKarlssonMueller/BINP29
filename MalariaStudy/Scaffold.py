#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
date:01.03.2022
name: Scaffold.py
author: Mirjam Karlsson-Müller
"""

import sys
"""
run in console with: python Scaffold.py input_file min_scaffold_size gc_content output_file

Input and output files are fastas, the scaffold and gc contents need to be numbers, whereas the gc content furthermore 
needs to be a percentage, i.e. a number between 1-100.
"""

#inputs. 
fastafile=sys.argv[1]    
min_size=int(sys.argv[2])
gc_content=float(int(sys.argv[3]))
outfile=sys.argv[4]
    

def GC(sequence):
    """
    Returns GC content of a nucleotide sequence. 
    Parameters
    ----------
    sequence : string
        string of nucleotides.

    Returns
    -------
    float
        Percentage of nucleotides being G or C.

    """
    gc=sequence.count("C")+sequence.count("G")
    total=gc+sequence.count("A")+sequence.count("T")
    return round(gc/total *100, 2)

with open(fastafile, 'r') as fasta:
    sequences=[]
    current_seq=""
    headers=[]
    for line in fasta:
        if line.startswith(">"):
            headers.append(line.strip("\n").split(" ")[0])
            if len(current_seq)>0:
                sequences.append(current_seq)
                current_seq=""
        else:
            current_seq=current_seq+line.strip("\n").upper()
            
fasta=dict()
for i in range(0,len(headers)-1):
    fasta[headers[i]]=sequences[i]
    
            
with open(outfile, 'w') as out:
    for ids in fasta:
        #Check size:
        if len(fasta[ids])>=min_size:
            #check gc content:
            gc=GC(fasta[ids])
            if gc<=gc_content:
                out.write('{}, GC: {}, Length: {}\n{}\n'.format(ids, gc, len(fasta[ids]), fasta[ids])) #write the output file.