
# coding: utf-8

# In[1]:

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE_sample = "barcelona_spain_sample.osm"
regex = re.compile(r'\b\S+\.?', re.IGNORECASE)

expected = ["Avinguda", "Carretera", "Camí", "Carrer", "Passatge", "Passeig", "Plaça", "Rambla", "Ronda", 
            "Travessera", "Via", "La"] #expected names in the dataset

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

# Search string for the regex. If it is matched and not in the expected list then add this as a key to the set.
def audit_street(street_types, street_name): 
    m = regex.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem): # Check if it is a street name
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile): # return the list that satify the above two functions
    osm_file = open(osmfile, "r", encoding = 'UTF-8')
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street(street_types, tag.attrib['v'])
    return street_types

pprint.pprint(audit(OSMFILE_sample)) # print the existing names

def string_case(s): # change string into titleCase except for UpperCase
    if s.isupper():
        return s
    else:
        return s.title()

# return the updated names
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

update_street = audit(OSMFILE_sample) 

# print the updated names
for street_type, ways in update_street.items():
    for name in ways:
        better_name = update_name(name, mapping)
        print (name, "=>", better_name)


# In[ ]:




# In[ ]:



