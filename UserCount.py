
# coding: utf-8

# In[ ]:

import xml.etree.cElementTree as ET
import pprint
import re

def get_user(element):
    return


def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if "user" in element.attrib:
            users.add(element.get('user'))
        
    return users


users = process_map('barcelona_spain.osm')
pprint.pprint(len(users))


# In[ ]:



