#!/usr/bin/python

import copy
import xml.etree.ElementTree as ElementTree
import sys

class NodeWrapper:
  def __init__(self,rootNode,defNode):
    self.rootNode = rootNode
    self.defNode = defNode

  # returns a 1-2 word description of this item
  # used for tab labels, button labels, etc.
  def getLabel(self):
    nodes = self.defNode.findall('label')
    if(len(nodes) == 0):
      return self.defNode.get('name')
    else:
      node = nodes[len(nodes)-1]
      return node.text % node.attrib

  # returns a phrase description of this item
  # used for page title or section header
  def getTitle(self):
    nodes = self.defNode.findall('title')
    if(len(nodes) == 0):
      return self.defNode.get('name')
    else:
      node = nodes[len(nodes)-1]
      return node.text % node.attrib

  def getListSummary(self):
    nodes = self.defNode.findall('listSummary')
    if(len(nodes) == 0):
      return self.getTitle()
    else:
      node = nodes[len(nodes)-1]
      return node.text % node.attrib

class BrowseWrapper(NodeWrapper):
  def __init__(self,rootNode,defNode):
    NodeWrapper.__init__(self,rootNode,defNode)
    self.typeNode = xref(rootNode,defNode.get('type'))

  def getLabel(self):
    labelNodes = self.typeNode.findall('label')
    if(len(labelNodes) == 0):
      return self.defNode.get('type')
    else:
      labelNode = labelNodes[len(labelNodes)-1]
      return labelNode.text % labelNode.attrib

  def getListSummary(self):
    nodes = self.typeNode.findall('listSummary')
    if(len(nodes) == 0):
      return self.getLabel()
    else:
      node = nodes[len(nodes)-1]
      return node.text % node.attrib

  def emitTab(self):
    print """
          <Tab label="%(label)s">
            <%(type)sBrowser url="/api/%(type)s" pollInterval={2000} />
          </Tab>
          """ % dict(label=self.getLabel(),type=self.defNode.get('type'))

def xref(rootNode,name):
  predicate = 'objType[@name=%s]' % (name)
  sys.stderr.write("predicate is %s\n" % predicate)
  defs1 = rootNode.findall("objType[@name='%s']" % (name))
  defs2 = rootNode.findall("relType[@name='%s']" % (name))
  if(len(defs1) > 0):
    return defs1[len(defs1)-1]
  elif(len(defs2) > 0):
    return defs2[len(defs2)-1]
  else:
    sys.stderr.write("Cannot locate definition of %s\n" % name)
    exit(1)

print """
const React = require('react');
const ReactDOM = require('react-dom');
const toolbox = require('react-toolbox');
const Tabs = toolbox.Tabs;
const Tab = toolbox.Tab;
const Dropdown = toolbox.Dropdown;
"""

argi = 0
for arg in sys.argv:
  if(argi > 0):
    print "// Debug: parsing "+arg+"\n"
    tree = ElementTree.parse(arg)
    root = tree.getroot()
    if root.tag != 'application':
        print "ERROR: XML root element is <%s> but expected <application>" % root.tag
        sys.exit(2);

    print """
class %(name)s extends React.Component {
    """ % root.attrib

    print """
  constructor() {
    super();
    this.state = {
      index: 1,
      fixedIndex: 1,
      inverseIndex: 1
    };
    this.handleTabChange = this.handleTabChange.bind(this);
    this.handleFixedTabChange = this.handleFixedTabChange.bind(this);
    this.handleInverseTabChange = this.handleInverseTabChange.bind(this);
  }

  handleTabChange(index) {
    this.setState({index});
    this.forceUpdate();
  };

  handleFixedTabChange(index) {
    this.setState({fixedIndex: index});
    this.forceUpdate();
  };

  handleInverseTabChange(index) {
    this.setState({inverseIndex: index});
    this.forceUpdate();
  };

  handleActive() {
    super.setState({
    index: 1,
    fixedIndex: 1,
    inverseIndex: 1
    });
    console.log('Special one activated');
  }  
    """

    print """
  render() {
    return (
      <div>
        <h1>%(title)s</h1>
        <Tabs index={this.state.index} onChange={this.handleTabChange}>
    """ % dict(name=root.get('name'),title=NodeWrapper(root,root).getTitle())

    for viewNode in root.findall('view'):        
        for browseNode in viewNode.findall('browse'):
            browse = BrowseWrapper(root,browseNode)
            browse.emitTab()

    print """
        </Tabs>
        </div>
    );
  }
}
    """

    for objType in root.findall('objType'):
        print """
var %(name)s = React.createClass({
  render: function() {
        """ % objType.attrib

        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
#            if 'type' in propertyType.attrib:
#                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                print """
    var %(name)s = this.getLabel_%(name)s();
                """ % propertyType.attrib
            else:
                print """
    var %(name)s = this.props.%(name)s;
                """ % propertyType.attrib

        print """
    return (
      <tr className="%(name)s">
        """ % objType.attrib

        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
#            if 'type' in propertyType.attrib:
#                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                print """
        <td>{%(name)s.label}</td>
                """ % propertyType.attrib
            else:
                print """
        <td>{%(name)s}</td>
                """ % propertyType.attrib

        print """
      </tr>
    );
  }
});
        """ % objType.attrib

    for objType in root.findall('objType'):
        print """
var %(name)sList = React.createClass({
  render: function() {
    var nodes = this.props.data.map(function(row) {
      return (
        <%(name)s """ % objType.attrib

        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
#            if 'type' in propertyType.attrib:
#                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                print """ %(name)sID={row.%(name)sID}""" % propertyType.attrib
            else:
                print """ %(name)s={row.%(name)s}""" % propertyType.attrib

        print """/>
      );
    }.bind(this));
    return (
      <div className="%(name)sList">
      <table>
        <tbody>
        {nodes}
        </tbody>
      </table>
      <div className="%(name)sListSummary">
      %(listSummary)s : {this.props.data.length}
      </div>
      </div>
    );
  }
});
        """ % dict(name=objType.get('name'),listSummary=NodeWrapper(root,objType).getListSummary())

    for objType in root.findall('objType'):
        print """
var %(name)sBrowser = React.createClass({
        """ % objType.attrib
        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib:
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                userDef = userDefs[len(userDefs)-1]
                print """
  %(name)sLoaded: function(rows) {
    var values = [];
    for(index=0;index<rows.length;index++) {
      var value = new %(name)s;
      value.setState({""" % propertyType.attrib
                index = 0
                for subProperty in userDef.findall('propertyType'):
                    if(index != 0): 
                      print ""","""
                    index += 1
                    print """ %(name)s: rows[index].%(name)s""" % subProperty.attrib
                print """});
      values.push(value);
    }
    this.setState({%(name)sValues: values});
  },
                """ % propertyType.attrib
        print """
  loadFromServer: function() {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
                """
        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib:
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                userDef = userDefs[len(userDefs)-1]
                print """
    $.ajax({
      url: 'api/%(name)s',
                """ % userDef.attrib
                print """
      dataType: 'json',
      cache: false,
      success: function(data) {
        this.%(name)sLoaded(data);
      }.bind(this),
      error: function(xhr, status, err) {
                """ % propertyType.attrib
                print """
        console.error('api/%(name)s', status, err.toString());
                """ % userDef.attrib
                print """
      }.bind(this)
    });
                """ % propertyType.attrib
        print """
  },
  handleSubmit: function(row) {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'POST',
      data: row,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: []""" % objType.attrib

        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib:
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                userDef = userDefs[len(userDefs)-1]
                print """, %(name)sValues: []""" % propertyType.attrib
        print """};
  },
  componentDidMount: function() {
    this.loadFromServer();
    setInterval(this.loadFromServer, this.props.pollInterval);
  },
  render: function() {
    return (
      <div className="%(name)sBrowser">
        <%(name)sList type="%(name)s" data={this.state.data}""" % dict(name=objType.get('name'))
        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib:
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                userDef = userDefs[len(userDefs)-1]
                print """ %(name)sValues={this.state.studentValues}""" % propertyType.attrib
        print """/>
      </div>
    );
  }
});

        """ % objType.attrib

    print """
ReactDOM.render(
  <%(name)s/>,
  document.getElementById('content')
);
    """ % root.attrib
  argi += 1
