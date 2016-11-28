#!/usr/bin/python

import copy
import xml.etree.ElementTree as ElementTree
import sys
import json

argi = 0
dbroot = 'jsondb/'
for arg in sys.argv:
  if(argi > 0):
    print "// Debug: parsing "+arg+"\n"
    tree = ElementTree.parse(arg)
    root = tree.getroot()
    if root.tag != 'application':
        print "ERROR: XML root element is <%s> but expected <application>" % root.tag
        sys.exit(2);

    for objType in root.findall('objType'):
        typeName = objType.get('name')
        objects = []
        fp = open(dbroot+typeName+'.json','w')
        if fp:
            print "Generating initial database for %s" % typeName
            id = 1
            for obj in root.findall('object'):
                if(obj.get('type') == typeName):
                    properties = dict(obj.attrib)
                    properties['id'] = id
                    for child in obj.findall('*'):
                        properties[child.tag] = child.text
                    objects.append(properties)
                    id += 1

            if len(objects) != 0:
                json.dump(objects,fp)
            fp.close()
  argi += 1
