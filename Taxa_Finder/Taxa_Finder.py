#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Title: Taxa_Finder.py
Date: 2022-03-09
Author: Mirjam Karlsson-Müller

Description: Finds the taxonomy lineage of one or more query /queries in the ncbi 
taxonomy database.  
    
    
List of functions:
    find_lineage: Finds lineage corresponding to a single query (string).

    
Procedure:
    1. Iterate through the queries, for each:
        a. The query is looked for in the file names.dmp, its corresponding ID
        is extracted. The scientific names and their corresponding IDs from names.dmp
        are saved.
        b. The script then looks for the query ID in the file nodes.dmp, finds the 
        corresponding parent ID, looks for that one in nodes.dmp, finds its parent
        ID etc until reaching the root of the taxonomic tree. The IDs are saved
        in a list.
        c. By going through the path list, the corresponding lineage is assembled
        as a string, one ID at the time. If input parameter -s or --short is given,
        then only nodes who are not marked as hidden by ncbi will be added to
        lineage.
    2. Lineage is printed in output file and/or console. The result is labelled with the query,
    to be able to distinguish the lineage. All results get printed in the same file.
    

Usage:
    Run in command line with:
    
    python Taxa_Finder.py -i INPUT ... [-o] [OUTFILE] [-s] [-p]
    
    --input INPUT, -i INPUT:        Query name, as string.
    
    --out [OUTFILE], -o [OUTFILE]: Lineage printed into specified outputfile.
                                    If output file not specified, but -o given, then 
                                    default file "Lineage.txt" is created.
    
    --short, -s:                    The lineage returned will only include entries not 
                                    flagged as hidden in the ncbi database.
    
    --print, -p:                    The lineage returned is printed to console.
    
    Note that printing to console and printing to outfile are not mutually exclusive.
    Both can be done, or neither.
    
Possible Bugs:
    1. Requires files names.dmp and nodes.dmp in working directory.
    2. If neither -p or -o are given, the script runs, but no output is given.
    
"""
#%%
"Using argparse to explain flags."
import argparse

parser = argparse.ArgumentParser(prog='Taxa_Finder',
                                 usage='%(prog)s -i INPUT [-s] [-p] -[o] [OUTPUT] ',
                                 description='Returns lineage of query based on ncbi`s taxonomy database.')
parser.add_argument('--input', '-i', nargs="+", 
                    help='Query name, either single string, or severl strings seperated by space.')
parser.add_argument('--out', '-o', nargs="?", default="Lineage.txt",
                    help='Lineage printed in specified output file. Default: Lineage.txt')
parser.add_argument('--short', '-s', action='store_true',
                    help='The lineage returned will only include entries not flagged as hidden by ncbi.')
parser.add_argument('--print', '-p', action='store_true',
                    help='The lineage is printed to console.')

args=parser.parse_args()

query=args.input
outfile=args.out


#%%
def find_lineage(query):
    """
    Finds the taxonomic lineage corresponding to a query.

    Parameters
    ----------
    query : string
        f.e. Human, Homo Sapiens, Mammalia etc.

    Returns
    -------
    Lineage: string
        taxonomic lineage leading from root to query.

    """
    "a. Find Query ID in names.dmp"
    #Initialize dictionary containing scientific names and corresponding ID
    names_dic=dict()

    with open("names.dmp", 'r') as names:
        for entry in names:
            #find query
            any_name=entry.split("\t|\t")[1]
            if any_name.upper().strip(" ")==query.upper().strip(" "):
                query_ID =entry.split("\t|\t")[0].strip(" ")
            #make name dictionary:
            #make sure to only use names flagged as scientific.
            if entry.split("\t|\t")[3][0:15]=="scientific name":  
                names_dic[entry.split("\t|\t")[0]]=entry.split("\t|\t")[1]            

    #If the query is not found in the file
    try: query_ID
    except NameError: query_ID=None

    if query_ID is None:
        print("The query could not be found. Please check your spelling or try with a different query. When using an informal name, it can help to use the scientific name instead.")
        quit()
    
    "b. Find Id in nodes.dmp, trace the path over parent ID back to root."

    #For additional information, s.a. rank or whether its included in shortened lineage.
    nodes_info=dict()
    #For ID/parent ID pairs.
    nodes_path=dict()

    #save nodes.dmp as dictionary
    with open("nodes.dmp",'r') as nodes:
        for entry in nodes:
            ID=entry.strip(" ").split("\t|\t")[0]
            parent_ID=entry.strip(" ").split("\t|\t")[1]
            rank=entry.strip(" ").split("\t|\t")[2]
            hidden_flag=entry.strip(" ").split("\t|\t")[10]
            nodes_info[ID]=[rank, hidden_flag]
            nodes_path[ID]=parent_ID
            
    #Find query ID, make path:
    root_found=False
    path=[]
    current_ID=query_ID
    while root_found==False:
        for ID in nodes_path:
            if current_ID==ID:
                #append the parent ID to path
                parent_ID=nodes_path[current_ID]
                #update current_ID
                current_ID=parent_ID
                if current_ID=="1":
                    root_found=True
                    break
                #If we are not at the root, append parent ID to path.
                path.append(parent_ID)
                
    "c. Assemble Output."

    lineage=""
    #right now the path goes from query back to root, we want the output reversed.

    for ID in reversed(path):
        #check if we want shortened path or the entire path:
        if args.short:
            #for the shortened path, we exclude the hidden_flags=1
            if path.index(ID)==0:
                if nodes_info[ID][1]=='0':
                    lineage+="{}.".format(names_dic[ID])
                    break
            if nodes_info[ID][1]=='0':
                lineage+="{}, ".format(names_dic[ID])
        #for the full path, we do not need to sort by hidden flags.
        else:
            if path.index(ID)==0:
                lineage+="{}.".format(names_dic[ID])
                break
            else:
                lineage+="{}, ".format(names_dic[ID])
        
    return(lineage)        

#%%

#Checking if input format is right.
if isinstance(query, list)==True:
    output=""
    for i in query:
        lineage=find_lineage(i)
        output+="Lineage for query {}: {}\n".format(i,lineage)
else:
    print("Query format not correct, use strings enclosed by "" or '', queries seperated by space. ")
    quit()

"Output."
#If output file is wished for:
if args.out:
    with open(outfile,'w') as out:
        out.write(output)
#If console output is wished for:           
if args.print:
    print(output)     
            