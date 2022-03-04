#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
date:04.03.2022
name:Superparser.py
author:Mirjam Karlsson-Müller

execute like:
python Superparser.py indirectory outfile
"""

from pathlib import Path
import sys


busco_seq_path=Path(sys.argv[1])
busco_seq_path=busco_seq_path.glob('*')
outfile=sys.argv[2]

busco_dict=dict()
species=["Pb","Pc","Pf","Pk","Pv","Py","Ht", "Tg"]
for i in species:
    busco_dict[i]=""

for busco_file in busco_seq_path:
    with open (busco_file,'r') as busco:
        for line in busco:
            if line.startswith(">"):
                header=line.strip(">").strip("\n")
                line=next(busco)
                busco_dict[header]+=line.strip("\n")

with open (outfile, 'w') as out:
    for species in busco_dict:
        out.write(">{}\n{}\n".format(species, busco_dict[species]))