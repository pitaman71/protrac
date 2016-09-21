#!/usr/bin/python

import copy
import xml.etree.ElementTree as ElementTree
import sys

print """
import json
import os
import time
from flask import Flask, Response, request

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
    app.run(port=int(os.environ.get("PORT", 3000)), debug=True)
"""
