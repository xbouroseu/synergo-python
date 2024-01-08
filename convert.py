# -*- coding: utf-8 -*-
#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import zipfile
import os
import tempfile
import shutil
import sys
from pathlib import Path, PurePath

# - Get the synergo file path
# - Create a temporary directory where we will store the copied files
# - Create a copy in .zip format
# - Extract the contents of the zip file and read the contents of the history.xml file
# - Parse the content of the history.xml file using the xml.etree module
# TODO support for do-while

Args = sys.argv
input_file_path = Args[1]
input_file_name = Path(input_file_path).parts[-1]
output_file_basename = Args[2] if len(Args)>2 else ".".join(input_file_name.split(".")[:-1])
use_temp = Args[3] if len(Args)>3 else True

def open_synergo_xml(filepath:str, use_temp:bool = True) -> str:
    # Create the temp path
    temp_path = ""
    if use_temp:
        temp_path = tempfile.mkdtemp()
    else:
        if "tmp00" not in os.listdir("./"):
            os.mkdir("tmp00")
        temp_path = "tmp00"
        
    print("Temp_path:", temp_path)
    
    file_Path = Path(filepath)
    filename = file_Path.parts[-1]
    
    # Make copy in .zip format and place it in the temporary directory
    zip_copy_path = PurePath(temp_path).joinpath(filename + ".zip")
    shutil.copy2(filepath, zip_copy_path)

    # Extract contents of history.xml file in the temporary directory
    zip_f = zipfile.ZipFile(zip_copy_path, "r")
    zip_contents_filenames = zip_f.namelist()
    xml_filename = [x for x in zip_contents_filenames if x.split(".")[-2]=="xml"][0]
    zip_f.extract(xml_filename, temp_path)
    zip_f.close()
    
    # Read xml file contents
    xml_file_temppath = PurePath(temp_path).joinpath(xml_filename)
    xml_fileIO = open(xml_file_temppath, "r", encoding="utf16")
    xml_file_text = xml_fileIO.read()
    xml_fileIO.close()
    xml_file_parsed = ET.fromstring(xml_file_text)

    ## - Remove the contents of the temporary directory so it can be deleted
    ## - Delete the temporary directory
    os.unlink(zip_copy_path)
    os.unlink(xml_file_temppath)
    os.rmdir(temp_path)  
    
    return xml_file_parsed

doc = open_synergo_xml(input_file_path)

## affirmative : list containing all the possible
##               [Yes-Like] inputs the user can give
##
## negative : list containing all the possible
##            [No-Like] inputs the user can give
##
## elements : Structure containing {key:value} pairs
##      where :
##          key = [element id]
##          value = list containing [element id]
##
## contents : Structure containing {key:value} pairs
##      where :
##          key = [element id]
##          value = [element content]
##
## connectors : Structure containg {key:value} pairs
##      where :
##          key = [connector id]
##          value = list containing [from,to] values
##                  where :
##                      from = root of connector
##                      to = connector destination
##
## sxeseis : Structure containg {key:value} pairs
##      where :
##          key = [element id]
##          value = Structure containing {id:to} pairs
##              where :
##                  id = [connector id]
##                  to = [connector destination]


affirmative = ["Yes","YES","yes","YeS","YEs","yeS","yES","NAI",u'\u039d\u0391\u0399']
negative = ["No","NO","no","nO","OXI",u'\u039f\u03a7\u0399']

elements = {}
contents = {}
connectors = {}
sxeseis = {}

## Iterate through all <event> elements in the .xml file
## Each <event> element contains sub-elements which describe
## every kind of action concerning it
##
## Example:
##
##      <event>
##          <id_event> [event id, which is unique] </id_event>
##          <time1> [time when event started] </time1>
##          <time2> [time when event ended] </time2>
##          <user> [username entered in the login screen] </user>
##          <action> [element action] </action>
##          <attribute> [event attribute] </attribute>
##          <typology />
##          <comments />
##          <added_by_user> [Boolean] </added_by_user>
##
## Explanation:
##      The algorithm below focuses around the <action> and <attribute>
##      elements of each <event> element.
##
##      The <action> element takes one of these values:
##          "Insert Entity": User inserts an object
##          "Change Concept Entity Text": User changes the content of a given element
##          "Insert Concept Relationship": User connects two given elements with
##                         a relationship which has a start(root) and an end(destination)
##          "Change Concept Relation text": User changes the text of a relationship between elements
##          "Concept arrow added": User changes the destination of a relationship
##          "Concept link added": User changes the root of a relationship
##          "Delete object": User deletes an object. Can be an element or a relationship
##          "Delete objects": User deletes many objects at once
##
##      The <attribute> element describes the targets of each event.
##          Example in the case of a "Insert Concept Relationship"
##          event then the <attribute> element would be like this:
##              [qualitative, qualitative(ID), [x=x_coordinate, y=y_coordinate], Root, Destination]
##              where ID: is the connector id between those Root and Destination
##
##      So the purpose of this algorithm is to identify what kind
##      of actions are done and it finally builds a Elements structure which contains
##      every element, which is present at the final form of the diagram, and their properties.

ev = doc.find("events")
events = ev.findall("event")

def get_cont(string,a,b):
    in_a = string.find(a)
    in_b = string.find(b)
    return string[in_a+1:in_b]

def get_id(string):
        return int(get_cont(string,"(",")"))

def is_note(str):
    return str.find("note")>-1

def is_text(str):
    return str.find("text_")>-1

for i in events:
    action = i.findtext("action")
    atr = i.findtext("attribute").strip("[]").rsplit(",")

    if action == "Insert Entity":
        kind = atr[0]
        idd = int(atr[len(atr)-1].lstrip())
        elements[idd] = [idd,kind] 
    elif action == "Change Concept Entity text":
        idd = int(get_cont(atr[0],"(",")"))
        contents[idd] = atr[1].lstrip()       
    elif action == "Change Concept Relationship text":
        connector_id = get_id(atr[0])
        text = atr[1].lstrip()
        if len((connectors)[connector_id])==3:
            connectors[connector_id][2] = text
        else:
            connectors[connector_id].append(text)       
    elif action == "Insert Concept Relationship":
        connector_id = get_id(atr[1])
        first = get_id(atr[5])
        last = get_id(atr[6])
        connectors[connector_id] = [first,last]
        if first not in sxeseis:
            sxeseis[first] = {connector_id:last}
        else:
            sxeseis[first][connector_id]=last       
    elif action == "Concept arrow added":
        con_id = get_id(atr[0])
        root_id = connectors[con_id][0]
        dest_id = get_id(atr[1])
        connectors[con_id][1] = dest_id
        sxeseis[root_id][con_id] = dest_id
    elif action == "Concept link added":
        con_id = get_id(atr[0])
        prev_root = connectors[con_id][0]
        new_root = get_id(atr[1])

        if len(sxeseis[prev_root])==1:
            del sxeseis[prev_root]
        else:
            del sxeseis[prev_root][con_id]

        if new_root not in sxeseis:
            sxeseis[new_root] = {}
        sxeseis[new_root][con_id] = connectors[con_id][1]
        connectors[con_id][0] = new_root               
    elif action == "Delete objects":
        conn_ids = []
        els = []

        for x in range(len(atr)):
            obj = atr[x]
            is_conn = atr[x].find("qualitative") > -1
            is_t = is_text(atr[x])
            is_n = is_note(atr[x])
            if is_conn:
                conn_ids.append(get_id(atr[x]))
            elif not (is_n or is_t):
                els.append(get_id(atr[x]))
            
        for x in conn_ids:
            if x in connectors:
                fir = connectors[x][0]
                las = connectors[x][1]

                del connectors[x]
                
                del sxeseis[fir][x]

                if len(sxeseis[fir].values()) == 0:
                    del sxeseis[fir]

        for x in els:
            if x in contents:
                del contents[x]
            
            if x in sxeseis:
                del sxeseis[x]

            del elements[x]               
    elif action == "Delete object":
        is_con = atr[0].find("qualitative")
        is_n = is_note(atr[0])
        is_t = is_text(atr[0])

        if not (is_n or is_t):
            id = get_id(atr[0])
            if is_con > -1:
                el = connectors[id][0]
                del connectors[id]
                del sxeseis[el][id]
            else:
                if id in contents:
                    del contents[id]

                if id in sxeseis:
                    del sxeseis[id]
                del elements[id]

## Errors Interface
Errors = ["There is no {0} element.","There are more than 1 {0} elements.\nId's: {1}",\
          "Decision ({0}) misses a Yes/No connection.","{0} Element is of not type 'Start-End'",\
          "Element ({0}) is connected to more than 1 Elements but is not of type 'Decision'."]

class StructureError(BaseException):
    global Errors
    def __init__(self,erid,obj):
        self.er_id = erid
        self.format = obj

    def __str__(self):
        return Errors[self.er_id].format(*self.format)

Elements = {}
for x in elements:
    if x in contents:
        elements[x].append(contents[x])
    else:
        elements[x].append("")

## - Build the basic Element structure ##
for x in elements:
    el = elements[x]
    Elements[x] = {}
    Elements[x]["id"] = el[0]
    Elements[x]["kind"] = el[1]
    Elements[x]["text"] = el[2]
    Elements[x]["To"] = []
##===========================================##

## - Append the next element to the 'To'
##  attribute and find Yes/No Roads
for x in sxeseis:
    el = Elements[x]
    r = sxeseis[x]
    kind = el["kind"]

    if kind == "Decision":
        el["To"] = {}
        for y in r:
            try:
                con_text = connectors[y][2]
                if con_text == "":
                    raise StructureError(2,[x])
            except:
                raise StructureError(2,[x])
            is_negative = con_text in negative
            if not is_negative:
                el["To"]["Yes"] = r[y]
            else:
                el["To"]["No"] = r[y]
    else:
        el["To"] = list(r.values())[0]
##================================================##

## - Find first element ##
first_el = [];

for x in Elements:
    el = Elements[x]
    is_first = True
    for y in connectors:
        if connectors[y][1] == x:
            is_first = False
            break

    if is_first:
        first_el.append(x);

if len(first_el)>1:
    if Elements[first_el[0]]["kind"] != "Start-End":
        raise StructureError(3,["Starting"])
    
    str_first_el = [str(x) for x in first_el]
    raise StructureError(1,["starting",",".join(str_first_el)])
elif len(first_el)==0:
    raise StructureError(0,["starting"]);

first_el = first_el[0]

if Elements[first_el]["kind"] != "Start-End":
    raise StructureError(3,["Starting"])

##===================================##

## - Find last element ##
last_el = [x for x in Elements if x not in sxeseis]

if len(last_el)>1:
    if Elements[last_el[0]]["kind"] != "Start-End":
        raise StructureError(3,["Ending"])
    str_last_el = [str(x) for x in last_el]
    raise StructureError(1,["ending",",".join(str_last_el)])
elif len(last_el)==0:
    raise StructureError(0,["ending"])

last_el = last_el[0]

## Add this to avoid confusion in further functions
Elements[last_el]["To"] = last_el;

if Elements[last_el]["kind"] != "Start-End":
    raise StructureError(3,["Ending"])
##====================================##


## Check for proper connections
for x in Elements:
    if Elements[x]["kind"]!="Decision" and x in sxeseis and len(sxeseis[x]) > 1:
        raise StructureError(4,[x]);


## previous,key_of,_print : Unused until now
def previous(index):
    roots = []

    for x in Elements:
        if Elements[x]["To"] == index:
            roots.append(x)

    return roots

def key_of(value,dic):
    for x in dic:
        if dic[x] == value:
            return x

def _print(obj):
    for x in obj:
        print(x," : ",obj[x])
##

## gen_skip : Function(index)
##     where index argument is the Element Id
##
## Functionality:
##     It goes through all the elements after the element given
##     until it finds a decision element where it stops
##
##     It returns a list with all the elements passed through (trace)
        
def gen_skip(index):
    el = Elements[index]
    kind = el["kind"]
    if kind=="Decision" or kind=="Loop":
        return [index]
    tr = []
    next = Elements[el["To"]]

    while next["kind"]!="Decision" and next["kind"]!="Loop" and next["id"]!=last_el:
        tr.append(next["id"])
        next = Elements[next["To"]]

    tr.append(next["id"])
    return tr

##=======================================================================##

## been : Structure consisting of {key:value} pairs
##     where key = [The Decision Element Id]
##     and value = True: [If element has been marked(met) before]
##                 False: [If not ^^]
##
## levels : Structure consisting of {key:value} pairs
##     where key = [The level of depth inside the tree]
##     and value = [A list with all the Decision Elements inside that level]
##
## decisions : List consisting of all the Decision Elements ("Loops" and "If")
##
## indent : Function(levels)
##     where levels = depth level
##
## Functionality:
##     Returns a number of tabs equals the number of levels
##
## find_level : Function(index)
##     where index = Element Id
##
## Functionality:
##     Returns the level of the Decision Element
##     defined by the [index] argument

been = {}
levels = {}
decisions = [x for x in Elements if Elements[x]["kind"]=="Decision"]
    
for y in decisions:
    been[y] = False

def indent(levels):
    return "\t"*levels

def find_level(index):
    for x in levels:
        if index in levels[x]:
            return x
        
##=======================================================================##

## ================ Traverse ==================##
## Traverse is the basic function which traverses
## through all the element tree to look for loops

def traverse(st,end,level):
    global been,levels,Elements
    
    el = Elements[st]
    next = el["To"]
    kind = el["kind"]
    
    if level not in levels:
        levels[level] = []

    if st==end:
        return 0
    
    if st!=end:
        if kind == "Decision":
            if been[st]==True:
                Elements[st]["kind"]="Loop"
                return -1
                
            if been[st] == False:
                levels[level].append(st)
                been[st]=True

            yes_road = gen_skip(next["Yes"])
            no_road = gen_skip(next["No"])
            meet = [y for y in yes_road if y in no_road]

            if len(meet)>0:
                return traverse(meet[0],end,level)
            else:
                l = traverse(next["Yes"],end,level+1)
                if l!=-1:
                    return traverse(next["No"],end,level-1)
                else:
                    return traverse(next["No"],end,level+1)
        elif kind == "Loop":
            return traverse(next["No"],end,level)
        else:
            return traverse(next,end,level)

## Call the traverse function to go through all
## the elements and identify the loops
        
traverse(first_el,last_el,0)

## _next : Function(id)
##     where id = element id
##
## Functionality:
##     returns the element after the element defined by the [id] argument

def _next(id):
    el = Elements[id]
    kind = el["kind"]

    if kind=="Decision":
        return _meet(el["To"]["Yes"],el["To"]["No"],id)
    elif kind=="Loop":
        return el["To"]["No"]
    if id==last_el:
        return id
    return el["To"]

##====================================================================#


## meet : Function(el1,el2,start)
##
## Functionality:
##     Returns the meeting point of the (el1,el2) elements which are
##     sub-elements of the Decision element defined by the [start] argument

def _meet(el1,el2,start):
    start_level = find_level(start)
    trace1 = _trace(el1,start_level)
    trace2 = _trace(el2,start_level)

    common = [y for y in trace1 if y in trace2]
    return common[0]

##====================================================================#


## Trace : Function(el,level)
##     where el = element id
##     and level = depth level
##
## Functionality:
##     Passes through all the elements after the element defined by the
##     [el] argument until it finds a decision which is is in the same
##     depth level defined by the [level] argument

def _trace(el,level):
    global last_el
    next = _next(el)
    found = False
    tr = [el,next]
    if Elements[next]["kind"]=="Decision":
        if find_level(next) == level:
            found=True
    while next!=last_el and found==False:
        next = _next(next)
        tr.append(next)
        if Elements[next]["kind"]=="Decision":
            if find_level(next) == level:
                found=True

    return tr

##=======================================================================##

## final_decisions : list containing all the Decision ("If") Elements
final_decisions = [x for x in decisions if Elements[x]["kind"]=="Decision"]

## Loop through all the decisions and add
## an attribute defining their meeting point
for x in final_decisions:
    el = Elements[x]
    el["meet"] = _meet(el["To"]["Yes"],el["To"]["No"],el)
    
## build : Function(start,end,level)
##     where start = [starting element id]
##           end = [ending element id]
##           level = [current depth level]
##
## Functionality:
##     Builds the corresponding text between the [start] and the [end]
##     elements and adds it to the Global [Text] variable
##
## Note:
##      If you un-comment the comments inside you will see the debug
##      process which prints every information passed through.

current = first_el

Text = ""
def build(start,end,level):
    global Text,last_el,first_el
    if start == first_el:
        start = Elements[first_el]["To"]
    el = Elements[start]
    kind = el["kind"]
    if start!=end:
        if kind !="Start-End":
            if kind=="Loop":
                #print 
                #print indent(level),"--Loop--",start," No: ",el["To"]["No"]," - ",end
                Text += indent(level) + "while " + el["text"] + ":\n"
                #print indent(level+1)," Yes-> ", el["To"]["Yes"]
                build(el["To"]["Yes"],start,level+1)
                #print indent(level)," No-> ", el["To"]["No"]
                build(el["To"]["No"],end,level)
            elif kind=="Decision":
                yes = el["To"]["Yes"]
                no = el["To"]["No"]
                meet = el["meet"]
                #print indent(level),"meet ",meet
                Text += indent(level) + "if " + el["text"] + ":\n"
                #print indent(level+1)," Yes-> ", el["To"]["Yes"]
                build(yes,meet,level+1)
                if meet!=no:
                    Text += indent(level) + "else:\n"
                    #print indent(level+1)," No-> ", el["To"]["No"]
                    build(no,meet,level+1)
                Text += "\n"
                #print indent(level)," Decision-> ", meet
                build(meet,end,level)
            elif kind!="Connector":
                Text += indent(level) + el["text"] + "\n"
                #print indent(level)," Element-> ", el["To"]
                build(el["To"],end,level)
            else:
                #print indent(level)," Connector-> ", el["To"]
                build(el["To"],end,level)

##=======================================================================##

## Call the build function with starting element the first element
## and ending element the last element, so it will pass through all
## the elements and build the final Text

build(first_el, last_el, 0)

## - Create the final file
ret = open( output_file_basename + ".txt", "w", encoding="utf-8")

## - Add the final text
ret.write(Text)
ret.close()

## - Rename to python extension
os.rename(output_file_basename + ".txt", output_file_basename + ".py")
