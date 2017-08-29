
# coding: utf-8

# In[3]:

import xml.etree.cElementTree as ET
import pprint
from collections import defaultdict

def count_tags(filename):
        # YOUR CODE HERE
    counts = defaultdict(int)
    for event, node in ET.iterparse(filename):
        if event == 'end': 
            counts[node.tag]+=1
        node.clear()             
    return counts


tags = count_tags('barcelona_spain.osm')
pprint.pprint(dict(tags))


# In[ ]:



