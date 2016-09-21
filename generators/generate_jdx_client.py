#!/usr/bin/python

import copy
import xml.etree.ElementTree as ElementTree
import sys

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
        <h1>%(name)s</h1>
        <Tabs index={this.state.index} onChange={this.handleTabChange}>
    """ % root.attrib

    for view in root.findall('view'):        
        for browse in view.findall('browse'):
            print """
          <Tab label="%(type)s">
            <%(type)sBrowser url="/api/%(type)s" pollInterval={2000} />
          </Tab>
            """ % browse.attrib

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
      </div>
    );
  }
});
        """ % objType.attrib

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
        <h1>List of %(name)s</h1>
        <%(name)sList data={this.state.data}""" % objType.attrib
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
