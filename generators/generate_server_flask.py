#!/usr/bin/python

import copy
import xml.etree.ElementTree as ElementTree
import sys

print """
import json
import os
import time
import re
from flask import Flask, Response, request

f = os.popen('ifconfig eth0')
tmp=f.read()
tmp=re.search('inet (\S+)',tmp)
hostIp = '0.0.0.0'
portNumber=int(os.environ.get("PORT", 3000))
if tmp != None:
    hostIp = tmp.expand(r'\\1')
    portNumber=80
app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))
"""

argi = 0
for arg in sys.argv:
  if(argi > 0):
    print "# Debug: parsing "+arg+"\n"
    tree = ElementTree.parse(arg)
    root = tree.getroot()
    if root.tag != 'application':
        print "ERROR: XML root element is <%s> but expected <application>" % root.tag
        sys.exit(2);
    objTypes = root.findall('objType')
    for objType in objTypes :
        print """
@app.route('/api/%(name)s', methods=['GET', 'ADD', 'EDIT', 'DELETE'])
def %(name)s_handler():
    items_before = []
    items_after = []
    try:
        f = open('%(name)s.json', 'r')
        items_before = json.loads(f.read())
    except:
        print "JSON database file %(name)s does not exist yet, will be created on the first POST"

    fields = request.form.to_dict()
    save = False
    if request.method == 'ADD':
        print "ADD %(name)s"
        new_item = fields
        new_item['id'] = int(time.time() * 1000)
        items_after = items_before
        items_after.append(new_item)
        save = True
    elif request.method == 'DELETE':
        print "DELETE %(name)s id="+fields['id']
        for item in items_before:
            if item['id'] != int(fields['id']):
                items_after.append(item)
        save = True
    elif request.method == 'EDIT':
        print "EDIT %(name)s id="+fields['id']
        for item in items_before:
            if item['id'] != int(fields['id']):
                items_after.append(item)
            else:
                new_item = fields
                new_item['id'] = int(fields['id'])
                items_after.append(new_item)
        save = True
    else:
        items_after = items_before

    if save:
        with open('%(name)s.json', 'w') as f:
            f.write(json.dumps(items_after, indent=4, separators=(',', ': ')))

    return Response(
        json.dumps(items_after),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )
        """ % objType.attrib

    relTypes = root.findall('relType')
    for relType in relTypes :
        print """
@app.route('/api/%(name)s', methods=['GET', 'POST'])
def %(name)s_handler():
    items = []
    try:
        f = open('%(name)s.json', 'r')
        items = json.loads(f.read())
    except:
        print "JSON database file %(name)s does not exist yet, will be created on the first POST"

    if request.method == 'POST':
        new_item = request.form.to_dict()
        new_item['id'] = int(time.time() * 1000)
        items.append(new_item)

        with open('%(name)s.json', 'w') as f:
            f.write(json.dumps(items, indent=4, separators=(',', ': ')))

    return Response(
        json.dumps(items),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )
        """ % relType.attrib

  argi = argi + 1

print """

if __name__ == '__main__':
    app.run(host=hostIp,port=portNumber, debug=True)
"""
