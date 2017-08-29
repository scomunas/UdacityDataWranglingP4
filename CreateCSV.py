
# coding: utf-8

# In[8]:

import csv
import codecs
import re
import xml.etree.cElementTree as ET
from unittest import TestCase

OSM_PATH = "barcelona_spain.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

mapping = {"A-2": "Carretera A-2",
           "Av.": "Avinguda",
           "Avenida": "Avinguda",
           "Avinguida": "Avinguda",
           "BP-1417": "Carretera BP-1417",
           "BV-2002": "Carretera BV-2002",
           "C./": "Carrer",
           "CALLE": "Carrer",
           "CARRETERA": "Carretera",
           "CL": "Carrer",
           "CRTA.": "Carretera",
           "Calle": "Carrer",
           "Caller": "Carrer",
           "Camino": "Camí",
           "CarrerAlt": "Carrer Alt",
           "Carrerde": "Carrer de",
           "PASEO": "Passeig",
           "Paseo": "Passeig",
           "Pl": "Plaça",
           "Pl,": "Plaça",
           "Pl.": "Plaça",
           "Pla": "Plaça",
           "Placeta": "Plaça",
           "Polígono": "Polígon",
           "Pomar": "Carrer Pomar",
           "Portaferrissa": "Avinguda Portaferrissa",
           "Pso.": "Passeig",
           "Ptge.": "Passatge",
           "RONDA": "Ronda",
           "Vía": "Via",
           "avinguda": "Avinguda",
           "c.": "Carrer",
           "carrer": "Carrer",
           "carretera": "Carretera",
           "passatge": "Passatge",
           "passeig": "Passeig",
           "plaça": "Plaça",
            }


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  

    if element.tag == 'node':
        for attrib in element.attrib:
            if attrib in NODE_FIELDS:
                node_attribs[attrib] = element.attrib[attrib]
        
        for child in element:
            node_tag = {}
            if LOWER_COLON.match(child.attrib['k']):
                node_tag['type'] = child.attrib['k'].split(':',1)[0]
                node_tag['key'] = child.attrib['k'].split(':',1)[1]
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                tags.append(node_tag)
            elif PROBLEMCHARS.match(child.attrib['k']):
                continue
            else:
                node_tag['type'] = 'regular'
                node_tag['key'] = child.attrib['k']
                node_tag['id'] = element.attrib['id']
                node_tag['value'] = child.attrib['v']
                tags.append(node_tag)
        
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        for attrib in element.attrib:
            if attrib in WAY_FIELDS:
                way_attribs[attrib] = element.attrib[attrib]
        
        position = 0
        for child in element:
            way_tag = {}
            way_node = {}
            
            if child.tag == 'tag':
                if LOWER_COLON.match(child.attrib['k']):
                    way_tag['type'] = child.attrib['k'].split(':',1)[0]
                    way_tag['key'] = child.attrib['k'].split(':',1)[1]
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)
                elif PROBLEMCHARS.match(child.attrib['k']):
                    continue
                else:
                    way_tag['type'] = 'regular'
                    way_tag['key'] = child.attrib['k']
                    way_tag['id'] = element.attrib['id']
                    way_tag['value'] = child.attrib['v']
                    tags.append(way_tag)
                    
            elif child.tag == 'nd':
                way_node['id'] = element.attrib['id']
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = position
                position += 1
                way_nodes.append(way_node)
        
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


def get_element(osm_file, tags=('node', 'way', 'relation')):
    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def string_case(s): # change string into titleCase except for UpperCase
    if s.isupper():
        return s
    else:
        return s.title()
    
def update_name(name, mapping):
    name = name.split(' ')
    for i in range(len(name)):
        if name[i] in mapping:
            name[i] = mapping[name[i]]
            name[i] = string_case(name[i])
        else:
            name[i] = string_case(name[i])
    
    name = ' '.join(name)
    return name
            
def update_way_tags(element):
    for child in element:
        if child['key'] == 'street':
            child['value'] = update_name(child['value'], mapping)
    return element
            

# Process XML and write CSV files
def process_map(file_in):
    nodes_file = open(NODES_PATH, 'w', encoding = 'UTF-8')
    nodes_tags_file = open(NODE_TAGS_PATH, 'w', encoding = 'UTF-8')
    ways_file = open(WAYS_PATH, 'w', encoding = 'UTF-8')
    way_nodes_file = open(WAY_NODES_PATH, 'w', encoding = 'UTF-8')
    way_tags_file = open(WAY_TAGS_PATH, 'w', encoding = 'UTF-8')

    nodes_writer = csv.DictWriter(nodes_file, NODE_FIELDS)
    node_tags_writer = csv.DictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
    ways_writer = csv.DictWriter(ways_file, WAY_FIELDS)
    way_nodes_writer = csv.DictWriter(way_nodes_file, WAY_NODES_FIELDS)
    way_tags_writer = csv.DictWriter(way_tags_file, WAY_TAGS_FIELDS)

    nodes_writer.writeheader()
    node_tags_writer.writeheader()
    ways_writer.writeheader()
    way_nodes_writer.writeheader()
    way_tags_writer.writeheader()

    for element in get_element(file_in, tags=('node', 'way')):
        el = shape_element(element)
        if el:
            if element.tag == 'node':
                nodes_writer.writerow(el['node'])
                node_tags_writer.writerows(el['node_tags'])
            elif element.tag == 'way':
                ways_writer.writerow(el['way'])
                way_nodes_writer.writerows(el['way_nodes'])
                el_fixed = update_way_tags(el['way_tags'])
                way_tags_writer.writerows(el_fixed)
                
    nodes_file.close()
    nodes_tags_file.close()
    ways_file.close()
    way_nodes_file.close()
    way_tags_file.close()

process_map(OSM_PATH)


# In[ ]:



