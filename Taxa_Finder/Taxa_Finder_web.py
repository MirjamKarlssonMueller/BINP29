#!/usr/bin/env python

from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def taxa():
	return render_template('Taxa_v04.html')

@app.route('/', methods=['POST'])
def show_lineage():
    query=request.form['query']
    query=query.split(",")
    if request.form.get('short-sequence')=="1":
        short=True
    else:
        short=False
    result=""
    taxonomy=dict()
    for q in query:
        lineage=find_lineage(q.strip(" "), short)
        if lineage.startswith("The query"):
            result+=lineage
        else:
            result+="The lineage for query <i>{}</i> is: {}</br></br>".format(q, lineage)
        taxonomy[q]=lineage
    if request.form.get('find-last-common-node')=="1":
        last_node=Find_common(taxonomy)
        if last_node==None:
            result+="</br> Cannot determine last node for a single query."
        else:
            result+="</br>The last common node between queries <i>{}</i> is: {}.".format(','.join(query), last_node)
    return render_template('Taxa_Finder_Out_v04.html', result=result)

def Find_common(taxonomy):
    """
    Finds the last common node in the taxonomic tree for all input queries.

    Parameters
    ----------
    taxonomy : dictionary
        contains queries as keys and lineage as values (list).

    Returns
    -------
    node: string

    """
    #If one of the lineages could not be found:
    for key in taxonomy:
        if taxonomy[key].startswith("The query"):
            return("No last node has been searched for, as one of the queries could not be found.")
    #Need taxonomy values to be lists:
    for key in taxonomy:
        taxonomy[key]=taxonomy[key].split(",")
    #Change values of taxonomy dictionary to sets
    taxonomy_set=dict()
    for key in taxonomy:
        taxonomy_set[key]=set(taxonomy[key])  
    
    values=list(taxonomy_set.values())
    #intersection between sets allows unknown number of queries.
    intersection=list(set.intersection(*values))
    #But it changes the order, so we need to go through one query to find "last"
    for element in taxonomy[list(taxonomy.keys())[0]]:
        #If the element is in the intersection, we update last node
        if element in intersection:
            last_node=element
        #If it is not, then the previous element was the last node.
        else:
            return(last_node)  

def find_lineage(query, short):
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
        return("The query <i>{}</i> could not be found. Please check your spelling or try with a different query. When using an informal name, it can help to use the scientific name instead.".format(query))
    
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
        if short==True:
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

if __name__== '__main__':
	app.run()