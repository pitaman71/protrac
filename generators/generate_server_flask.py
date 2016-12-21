#!/usr/bin/python

import copy
import xml.etree.ElementTree as ElementTree
import sys

dbroot = 'jsondb/'

def translate_infix(operation,operands):
    count = 0
    result = '('
    for operand in operands:
        if count > 0:
            result += ' '
            result += operation
            result += ' '
        result += operand
        count += 1
    result += ')'
    return result

def translate_call(operation,operands):
    count = 0
    result = operation
    result += '('
    for operand in operands:
        if count > 0:
            result += ','
        result += operand
        count += 1
    result += ')'
    return result

def translate_expr(expr):
    operands = expr.findall('*')
    values = []
    for operand in operands:
        values.append(translate_expr(operand))
    if(expr.tag == 'op'):
        if(expr.get('name') == 'eq'):
            return translate_infix('==',values)
        elif(expr.get('name') == 'ne'):
            return translate_infix('!=',values)
        elif(expr.get('name') == 'gt'):
            return translate_infix('>',values)
        elif(expr.get('name') == 'ge'):
            return translate_infix('>=',values)
        elif(expr.get('name') == 'lt'):
            return translate_infix('<',values)
        elif(expr.get('name') == 'le'):
            return translate_infix('<=',values)
        elif(expr.get('name') == 'add'):
            return translate_infix('+',values)
        elif(expr.get('name') == 'sub'):
            return translate_infix('-',values)
        elif(expr.get('name') == 'mul'):
            return translate_infix('*',values)
        elif(expr.get('name') == 'div'):
            return translate_infix('/',values)
        elif(expr.get('name') == 'mod'):
            return translate_infix('%',values)
        else:
            return translate_call(expr.get('name'),values)
    elif(expr.tag == 'ref'):
        return "%s.%s" % ('context',expr.get('symbol'))
    elif(expr.tag == 'field'):
        result = values[0]
        result += '.'
        result += expr.get('name')
        return result
    elif(expr.tag == 'exists'):
        result = """(count(context,'%s','%s',lambda context: %s) > 0)""" % (expr.get('symbol'),expr.get('type'),values[0])
        return result
    return 'False'

print """
import json
import os
import time
import re
import requests
from flask import Flask, Response, request
from flask.ext.cors import cross_origin
import jwt
import base64
from functools import wraps
from flask import Flask, request, jsonify, _request_ctx_stack
from werkzeug.local import LocalProxy

f = os.popen('ifconfig eth0')
tmp=f.read()
tmp=re.search('inet (\S+)',tmp)
hostIp = '0.0.0.0'
portNumber=int(os.environ.get("PORT", 3000))
if tmp != None:
    hostIp = tmp.expand(r'\\1')
    portNumber=80
current_user = LocalProxy(lambda: _request_ctx_stack.top.current_user)
app = Flask(__name__, static_url_path='', static_folder='public')
app.add_url_rule('/', 'root', lambda: app.send_static_file('index.html'))
#CORS(app)

# Authentication attribute/annotation
def authenticate(error):
  resp = jsonify(error)

  resp.status_code = 401

  return resp

def requires_auth(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    auth = request.headers.get('Authorization', None)
    if not auth:
      return authenticate({'code': 'authorization_header_missing', 'description': 'Authorization header is expected'})

    parts = auth.split()

    if parts[0].lower() != 'bearer':
      return {'code': 'invalid_header', 'description': 'Authorization header must start with Bearer'}
    elif len(parts) == 1:
      return {'code': 'invalid_header', 'description': 'Token not found'}
    elif len(parts) > 2:
      return {'code': 'invalid_header', 'description': 'Authorization header must be Bearer + \s + token'}

    token = parts[1]
    try:
        payload = jwt.decode(
            token,
            base64.b64decode('F5mgKJ3iHiXQDu3V9BrparcLMw_rLPrLHG8gk3W361va2Ai3tloabqumR6rP-NQb'.replace("_","/").replace("-","+")),
            audience='Iij39J1gGximSmXEyNK7KMrR53oEgfpD'
        )
    except jwt.ExpiredSignature:
        return authenticate({'code': 'token_expired', 'description': 'token is expired'})
    except jwt.InvalidAudienceError:
        return authenticate({'code': 'invalid_audience', 'description': 'incorrect audience, expected: Iij39J1gGximSmXEyNK7KMrR53oEgfpD'})
    except jwt.DecodeError:
        return authenticate({'code': 'token_invalid_signature', 'description': 'token signature is invalid'})

    _request_ctx_stack.top.current_user = user = payload
    return f(*args, **kwargs)

  return decorated

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

    print """
def authorize_action(typeName,opName,context):""",
    for objType in objTypes :
        print """
    if(typeName == '%(name)s'):""" % objType.attrib,
        actions = objType.findall('action')
        for action in actions:
            print """
        if(opName == '%(proto)s'):""" % action.attrib,
            exprs = action.findall('restrict/*')
            for expr in exprs:
                print """
            if not (%s): return False""" % translate_expr(expr),
            print """
            return True""" % action.attrib,
        print """
        return True""",

    print """
    return False""" % objType.attrib,

    print """
def filter_action(typeName,opName,context):""",
    for objType in objTypes :
        print """
    if(typeName == '%(name)s'):""" % objType.attrib,
        actions = objType.findall('action')
        for action in actions:
            print """
        if(opName == '%(proto)s'):""" % action.attrib,
            exprs = action.findall('filter/*')
            for expr in exprs:
                print """
            if not (%s): return False""" % translate_expr(expr),
            print """
            return True""" % action.attrib,
        print """
        return True""",

    print """
    return False""" % objType.attrib,

    print """
def filter_item(typeName,context):""",
    for objType in objTypes :
        print """
    if(typeName == '%(name)s'):""" % objType.attrib,
        exprs = objType.findall('filter/*')
        for expr in exprs:
            print """
        if not (%s): return False""" % translate_expr(expr),
        print """
        return True""" % action.attrib,


    print """
    return False""" % objType.attrib,


    for objType in objTypes :
        print """
@app.route('/api/%(name)s', methods=['BROWSE', 'ADD', 'EDIT', 'DELETE'])
@cross_origin(headers=['Content-Type', 'Authorization'])
@requires_auth
def %(name)s_handler():
    items_before = []
    items_after = []
    try:
        f = open('%(dbroot)s%(name)s.json', 'r')
        items_before = json.loads(f.read())
    except:
        print "JSON database file %(name)s does not exist yet, will be created on the first POST"

    fields = request.form.to_dict()
    save = False
    session = dict()
    session['loggedIn'] = request.headers.has_key('Authorization')

    print "Token = %%s\\n" %% _request_ctx_stack.top.current_user
    parts = request.headers.get('Authorization',None).split()
    url = "https://pitaman.auth0.com/tokeninfo?id_token=%%s" %% parts[1]
    data = dict({ "Content-Type": "application/json" })
    response = requests.get(url, data=data)
    if(response.ok):
        jData = json.loads(response.content)
        print "Authorized User = %%s\\n" %% jData
        session['email'] = jData[u'email']
        print "Confirmed Email = %%s\\n" %% session['email']
    else:
        return Response("Unable to cross reference authorization token",status=401,headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        })

    if not authorize_action('%(name)s',request.method,dict(session=session)):
        message = "User does not have permission to perform operation %%s on type %%s" %% (request.method,'%(name)s')
        print message
        return Response(message,status=403,headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        })

    outcome = 'succeed'
    if request.method == 'ADD':
        print "ADD %(name)s"
        new_item = fields
        new_item['id'] = int(time.time() * 1000)
        items_after = items_before
        items_after.append(new_item)
        outcome = filter_action('%(name)s',request.method,dict(item=new_item,session=session)) ? 'save' : 'fail'
    elif request.method == 'DELETE':
        print "DELETE %(name)s id="+fields['id']
        for item in items_before:
            if item['id'] != int(fields['id']):
                items_after.append(item)
            else:
                outcome = filter_action('%(name)s',request.method,dict(item=item,session=session)) ? 'save' : 'fail'
            if outcome == 'fail':
                break
    elif request.method == 'EDIT':
        print "EDIT %(name)s id="+fields['id']
        for item in items_before:
            if item['id'] != int(fields['id']):
                items_after.append(item)
            else:
                new_item = fields
                new_item['id'] = int(fields['id'])
                items_after.append(new_item)
                outcome = filter_action('%(name)s',request.method,dict(item=new_item,session=session)) ? 'save' : 'fail'
            if outcome == 'fail':
                break
    else:
        items_after = items_before

    if outcome == 'save':
        with open('%(dbroot)s%(name)s.json', 'w') as f:
            f.write(json.dumps(items_after, indent=4, separators=(',', ': ')))

    if outcome != 'succeed' and outcome != 'save':
        message = "User does not have permission to perform operation %%s on type %%s" %% (request.method,'%(name)s')
        print message
        return Response(message,status=403,headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        })

    items_filtered = []
    for item in items_after:
        if(filter_item('%(name)s',dict(session=session,item=item)):
            item['visible'] = True
            items_filtered.push(item)
        else:
            new_item = dict(visible=False,id=item['id'])
            items_filtered.push(item)

    return Response(
        json.dumps(items_filtered),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )
        """ % dict(name=objType.get('name'),dbroot=dbroot)

    relTypes = root.findall('relType')
    for relType in relTypes :
        print """
@app.route('/api/%(name)s', methods=['GET', 'POST'])
def %(name)s_handler():
    items = []
    try:
        f = open('%(dbroot)s%(name)s.json', 'r')
        items = json.loads(f.read())
    except:
        print "JSON database file %(name)s does not exist yet, will be created on the first POST"

    if request.method == 'POST':
        new_item = request.form.to_dict()
        new_item['id'] = int(time.time() * 1000)
        items.append(new_item)

        with open('%(dbroot)s%(name)s.json', 'w') as f:
            f.write(json.dumps(items, indent=4, separators=(',', ': ')))

    return Response(
        json.dumps(items),
        mimetype='application/json',
        headers={
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
    )
        """ %  dict(name=relType.get('name'),dbroot=dbroot)

  argi = argi + 1

print """

if __name__ == '__main__':
    app.run(host=hostIp,port=portNumber, debug=True)
"""
