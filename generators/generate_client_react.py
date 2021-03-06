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
  def getLabelItem(self):
    nodes = self.defNode.findall('labelItem')
    if(len(nodes) == 0):
      return self.defNode.get('name')
    else:
      node = nodes[len(nodes)-1]
      result = ""
      for child in node.iter():
        if child != node:
          result += ElementTree.tostring(child)
      return result % node.attrib

  # returns a 1-2 word description of (lists of) this kind of item
  # used for tab labels, button labels, etc.
  def getLabelList(self):
    nodes = self.defNode.findall('labelList')
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

class PropertyWrapper(NodeWrapper):
  def __init__(self,rootNode,defNode):
    NodeWrapper.__init__(self,rootNode,defNode)
    self.typeNode = xref(rootNode,defNode.get('type'),False)

  def emitFormElement(self):
      if(self.typeNode is not None):
        print """
        <Dropdown
          auto
          onChange={this.handle%(name)sChange}
          source={%(name)sValues}
          value={this.state.editorValues.%(name)s}
          label="%(label)s"
        />    """ % dict(name=self.defNode.get('name'),label=NodeWrapper(root,self.defNode).getLabelList(),type=self.typeNode.get('name'))
      elif(self.defNode.get('type') == 'StringLabel'):
        print """<Input type="text" multiline={false} onChange={this.handle%(name)sChange} label="%(label)s" value={this.state.editorValues.%(name)s}/>""" % dict(name=self.defNode.get('name'),label=self.getLabelList())
      elif(self.defNode.get('type') == 'StringComment'):
        print """<Input type="text" multiline={true} onChange={this.handle%(name)sChange} label="%(label)s" value={this.state.editorValues.%(name)s}/>""" % dict(name=self.defNode.get('name'),label=self.getLabelList())

class BrowseWrapper(NodeWrapper):
  def __init__(self,rootNode,defNode):
    NodeWrapper.__init__(self,rootNode,defNode)
    self.typeNode = xref(rootNode,defNode.get('type'),True)

  def getLabelList(self):
    labelNodes = self.typeNode.findall('labelList')
    if(len(labelNodes) == 0):
      return self.defNode.get('type')
    else:
      labelNode = labelNodes[len(labelNodes)-1]
      return labelNode.text % labelNode.attrib

  def getListSummary(self):
    nodes = self.typeNode.findall('listSummary')
    if(len(nodes) == 0):
      return self.getLabelList()
    else:
      node = nodes[len(nodes)-1]
      return node.text % node.attrib

  def emitTab(self):
    print """
          <Tab label="%(label)s">
            <%(type)sBrowser url="/api/%(type)s" pollInterval={5000} />
          </Tab>
          """ % dict(label=self.getLabelList(),type=self.defNode.get('type'))

def xref(rootNode,name,mandatory):
  predicate = 'objType[@name=%s]' % (name)
  defs1 = rootNode.findall("objType[@name='%s']" % (name))
  defs2 = rootNode.findall("relType[@name='%s']" % (name))
  if(len(defs1) > 0):
    return defs1[len(defs1)-1]
  elif(len(defs2) > 0):
    return defs2[len(defs2)-1]
  elif mandatory:
    raise Exception("Cannot locate definition of %s\n" % name)
  else:
    return None

print """
const React = require('react');
const ReactDOM = require('react-dom');
const toolbox = require('react-toolbox');
const Redux = require('redux');
const Auth0Lock = require('auth0-lock');

const Input = toolbox.Input;
const Tabs = toolbox.Tabs;
const Tab = toolbox.Tab;
const Table = toolbox.Table;
const Dropdown = toolbox.Dropdown;
const Button = toolbox.Button;
const Dialog = toolbox.Dialog;

class AuthService {
  constructor(clientId, domain) {
    // Configure Auth0
    var searchParams = window.location.search || ''
    this.lock = new Auth0Lock.default(clientId, domain, {
      auth: {
        redirectUrl: 'http://localhost:3000/'+searchParams,
        responseType: 'token'
      }
    })
    // Add callback for lock `authenticated` event
    this.lock.on('authenticated', this._doAuthentication.bind(this))
    // binds login functions to keep this context
    this.login = this.login.bind(this)
  }

  _doAuthentication(authResult) {
    // Saves the user token
    this.setToken(authResult.idToken)
    // navigate to the home route
    //browserHistory.replace('/home')
  }

  login() {
    // Call the show method to display the widget.
    this.lock.show()
  }

  loggedIn() {
    // Checks if there is a saved token and it's still valid
    return !!this.getToken()
  }

  setToken(idToken) {
    // Saves user token to local storage
    localStorage.setItem('id_token', idToken)
  }

  getToken() {
    // Retrieves the user token from local storage
    return localStorage.getItem('id_token')
  }

  logout() {
    // Clear user token and profile data from local storage
    localStorage.removeItem('id_token');
  }
}

const auth = new AuthService('Iij39J1gGximSmXEyNK7KMrR53oEgfpD', 'pitaman.auth0.com');

$.ajaxSetup({
  'beforeSend': function(xhr) {
    if (auth.loggedIn()) {
      xhr.setRequestHeader('Authorization',
        'Bearer ' + auth.getToken());
    }
  }
});

class Login extends React.Component {
  render() {
    const { auth } = this.props
    return (
      <div className={styles.root}>
        <h2>Login</h2>
        <ButtonToolbar className={styles.toolbar}>
          <Button bsStyle="primary" onClick={auth.login.bind(this)}>Login</Button>
        </ButtonToolbar>
      </div>
    )
  }
}

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

    # create Redux store
    for objType in root.findall('objType'):
      print """
        const initial%(name)s = { items: [] };
        var store%(name)s = Redux.createStore(reduce%(name)s,initial%(name)s);
      """ % objType.attrib

    # create Redux actions
    for objType in root.findall('objType'):
      print """
        function status%(name)s(status) {
          return {
            type: 'STATUS',
            status: status
          }
        }
        function async%(name)s(items) {
          return {
            type: 'ASYNC',
            items: items
          }
        }
        function logout%(name)s(items) {
          return {
            type: 'LOGOUT',
            items: items
          }
        }
      """ % objType.attrib

    # create Redux reducers
    for objType in root.findall('objType'):
      print """
        function reduce%(name)s(state, action) {
          switch (action.type) {
            case 'STATUS': 
              var newState = Object.assign({}, state);
              newState.status = action.status;
              return newState;
            case 'ASYNC': 
              var newState = Object.assign({}, state);
              newState.items = action.items;
              return newState;
            case 'LOGOUT': 
              return { state: 'loggedOut'};
            default:
              return state;
          }
        };
      """ % objType.attrib

    # app representative class
    print """
class %(name)sApp extends React.Component {
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
  };

  componentDidMount() {
    this.loadFromServer();
    setInterval(this.loadFromServer, this.props.pollInterval);
  };

  loadFromServer() {
    """
    for objType in root.findall('objType'):
      print """
    var idToken = "";
    if(!auth.loggedIn()) {
      store%(name)s.dispatch(status%(name)s('loggedOut'));
    } else {
      store%(name)s.dispatch(status%(name)s('synchronizing'));
      idToken = auth.getToken();
      $.ajax({
        url: 'api/%(name)s',
        type: 'BROWSE',
        dataType: 'json',
        cache: false,
        headers: { 'xxAuth': idToken },
        success: function(data) {
          // alert('Async state update receieved for %(name)s');
          store%(name)s.dispatch(async%(name)s(data));
          store%(name)s.dispatch(status%(name)s('upToDate'));
        }.bind(this),
        error: function(xhr, status, err) {
          store%(name)s.dispatch(status%(name)s(err.toString()));
          //console.error('api/%(name)s', status, err.toString());
        }.bind(this)
      });
    }
      """ % objType.attrib

    print """
  };
  doLogin() {
    auth.login(this);
    this.setState({loggedIn: true});
  };
  doLogout() {
    auth.logout(this);
    """ % dict(name=root.get('name'),title=NodeWrapper(root,root).getTitle())

    for objType in root.findall('objType'):
      print """
    store%(name)s.dispatch(logout%(name)s());
            """ % objType.attrib

    print """
    this.setState({loggedIn: false});
  };
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
          <Tab label="Login/Logout">
            <Button bsStyle="primary" onClick={this.doLogin.bind(this)} disabled={auth.loggedIn()}>Login</Button>
            <Button bsStyle="primary" onClick={this.doLogout.bind(this)} disabled={!auth.loggedIn()}>Logout</Button>
            <h2>Token</h2>
            <pre>
            {auth.loggedIn() ? auth.getToken().toString() : "Not Logged In"}
            </pre>
          </Tab>
        </Tabs>
        </div>
    );
  }
}
    """

    print """
      const renderItem = function(item) {
    """

    typeIndex = 0
    for objType in root.findall('objType'):
        if(typeIndex == 0):
          print """if(item.editorType == '%(name)s') {""" % objType.attrib
        else:
          print """} else if(item.editorType == '%(name)s') {""" % objType.attrib
        print """
          var id = "";
          if('id' in item) {
            id = item.id;
          }
          return <%(name)sInspector editorActive="true" id={id}""" % objType.attrib

        print """ editorMode={item.editorMode} onPushInspector={this.pushInspector} onPopInspector={this.popInspector} onUpdate={this.handleUpdate} onCancel={this.handleCancel}/>""" % objType.attrib
        typeIndex += 1
    print """}"""

    print """
      };
    """

    for objType in root.findall('objType'):
      print """
      const %(name)sSelectorSource = function() {
        var rows = store%(name)s.getState().items;
        var items = [];
        for(index=0;index<rows.length;index++) {
          var item = { value: rows[index].id };
          item.label = '%(label)s'; """ % dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelItem())
      for subProperty in objType.findall('propertyType'):
        print """    item.label = item.label.replace(/<%(name)s\s*\/>/g,rows[index].%(name)s);\n""" % subProperty.attrib
      print """
          items.push(item);
        }
        items.push({ value: "+", label: 'NEW %(name)s'});
        return items;
      };
                """ % objType.attrib

    # objType representative class
    for objType in root.findall('objType'):
        print """
var %(name)s = React.createClass({
        """ % objType.attrib
        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib: 
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                userDef = userDefs[len(userDefs)-1]
                print """
  getLabel_%(name)s: function() {
    var selectedValue = store%(type)s.getState().items.find(function(item) { return item.id == this.state.%(name)s; }.bind(this));
    if(selectedValue) {          
            var label = '%(label)s'; """ % dict(name=propertyType.get('name'),type=propertyType.get('type'),label=NodeWrapper(root,userDef).getLabelItem())
                for subProperty in userDef.findall('propertyType'):
                  print """    label = label.replace(/<%(name)s\s*\/>/g,selectedValue.%(name)s);\n""" % subProperty.attrib
                print """
      return label;
    } else {
      return '';
    }
  },                  """ % propertyType.attrib

        print """
  getTableRow: function() {
        var result = {};
        """ 
        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib: 
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                userDef = userDefs[len(userDefs)-1]
                print """
        result['%(name)s'] = this.getLabel_%(name)s();
                """ % propertyType.attrib
            else:
                print """
        result['%(name)s'] = this.props.%(name)s;
                """ % propertyType.attrib
        print """
        return result;
  },
        """
        print """
  getInitialState: function() {
      return {"""
        count = 0
        for propertyType in objType.findall('propertyType'):
          if count != 0:
            print """, """
          count += 1
          print """%(name)s: this.props.%(name)s""" % propertyType.attrib
        print """
      };
  },
  render: function() {
        """ % objType.attrib

        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib:
                propTypeName = propertyType.get('type')
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

    # objType Table Model
    for objType in root.findall('objType'):
        print 'const %(name)sModel = {\n' % objType.attrib
        count = 0
        for propertyType in objType.findall('propertyType'):
            if count > 0:
              print ',\n'
            propTypeName = ''
#            if 'type' in propertyType.attrib:
#                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            print '%(name)s: { type: String }' % propertyType.attrib
            count += 1
        print '};\n'

    # objType List class
    for objType in root.findall('objType'):
        print """
var %(name)sList = React.createClass({
  render: function() {
    var nodes = this.props.data.map(function(row) {
      return (
        <%(name)s """ % objType.attrib

        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib:
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
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

    # objType Table class
    for objType in root.findall('objType'):
        print """
var %(name)sTable = React.createClass({
  getInitialState: function() {
    return {selected: []};
  },
  handleSelect: function(selected) {
    this.setState({selected: selected});
    this.props.handleSelect(selected);
  },
  render: function() {
    var rows = this.props.data.map(function(properties) {
        var merged = {};
        for(var propName in properties) {
          merged[propName] = properties[propName];
        }
        for(var propName in this.props) {
          if(propName.endsWith('Values')) {
            merged[propName] = this.props[propName];
          }
        }
        var row = new %(name)s(merged);
        return row.getTableRow();
    }.bind(this));
    return (
        <Table selectable multiSelectable="" model={%(name)sModel} onSelect={this.handleSelect} source={rows} selected={this.state.selected}/>
    );
  }
});
        """ % objType.attrib

    for objType in root.findall('objType'):
        print """
var %(name)sBrowser = React.createClass({
        """ % objType.attrib
        print """
  loadFromServer: function() {
    var idToken = "";
    if(auth.loggedIn()) {
      idToken = auth.getToken();
    }
    $.ajax({
      url: 'api/%(name)s',
      type: 'BROWSE',
      dataType: 'json',
      cache: false,
      headers: { 'xxAuth': idToken },
      success: function(data) {
        if(this.isMounted()) {
          this.setState({data: data});
        }
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('api/%(name)s', status, err.toString());
      }.bind(this)
    });
                """ % objType.attrib
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
      type: 'BROWSE',
      dataType: 'json',
      cache: false,
      headers: { 'xxAuth': idToken },
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
  handleUpdate: function(typeName,data) {
      this.setState({data: data});
  },
  getInitialState: function() {
    return { selected: [], data: []""" % dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelList())
        print """ };
  },
  hasSelected: function() {
    return this.state.selected.length > 0;
  },
  getSelected: function() {
    return this.state.data[this.state.selected[0]];
  },
  loadFromStore: function() {
      var state = store%(name)s.getState();
      this.setState({ status: state.status, data: state.items });
  },
  componentDidMount: function() {
    // this.loadFromServer();
    // setInterval(this.loadFromServer, this.props.pollInterval);
    this.loadFromStore();
    this.unsubscribe = store%(name)s.subscribe(() => {
      //alert('Async update reached %(name)sBrowser with '+state.items.length+' items');
      if(this.isMounted()) {
        this.loadFromStore();
      }
    });    
  },
  componentWillUnmount: function() {
    this.unsubscribe();
  },
  handleSelect: function (selected) {
    this.setState({selected: selected});
  },
  render: function() {
    return (
      <div class="%(name)sBrowser Browser">
        <div class="%(name)sBrowserStatus BrowserStatus"><i>{this.state.status}</i></div>
        <%(name)sTable type="%(name)s" handleSelect={this.handleSelect} data={this.state.data}""" % dict(name=objType.get('name'))
        print """/>
          <%(name)sEditor hasSelected={this.hasSelected} getSelected={this.getSelected} onUpdate={this.handleUpdate} """ % dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelList())
        print """/>
      </div>
    );
  }
});

        """ % objType.attrib

        # objType Inspector class
        print """
var %(name)sInspector = React.createClass({
            """ % objType.attrib

        for propertyType in objType.findall('propertyType'):
            print """      
  handle%(name)sChange: function(value) {
    var newEditorValues = this.state.editorValues;
    newEditorValues.%(name)s = value;
    this.setState({editorValues: newEditorValues});
    if(value == "+") {
      var inspector = { editorType: '%(type)s', editorMode: "ADD", editorField: "%(name)s", onPushInspector: this.pushInspector, onPopInspector: this.popInspector};
      this.pushInspector(inspector);      
    }
  },""" % propertyType.attrib

        print """
  getInitialState: function() {
    var initialValues = {
        """
        propCount = 0
        for propertyType in objType.findall('propertyType'):
          if propCount > 0: 
            print ""","""
          print """%(name)s: ''""" % propertyType.attrib
          propCount += 1
        print """
    };

    if('id' in this.props) {
        var state = store%(name)s.getState();
        var myItem = state.items.find(function(item) { return item.id == this.props.id; }.bind(this));
        if(myItem) {
          //alert('getInitialState reached %(name)sInspector with '+state.items.length+' items of which id '+this.props.id+' is found');
          initialValues = myItem;
              """ % objType.attrib

        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib:
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                userDef = userDefs[len(userDefs)-1]
                print """initialValues.%(name)s = Number(initialValues.%(name)s);""" % propertyType.attrib

        print """
        } else {
          //alert('getInitialState ignored by %(name)sInspector with '+state.items.length+' items of which id '+this.props.id+' cannot be found');
        }
    }

    return { id: this.props.id, actions: [
    { label: "Cancel", onClick: this.handleCancel },
    { label: this.props.editorMode+" %(label)s", onClick: this.handleSubmit }
                      ], 
             editorActive: true, editorValues: initialValues """ % dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelList())

        print """};
  },
  handleSubmit: function() {
    var idToken = "";
    if(auth.loggedIn()) {
      idToken = auth.getToken();
    }
    $.ajax({
      url: 'api/%(name)s',
      dataType: 'json',
      type: this.props.editorMode,
      data: this.state.editorValues,
      headers: { 'xxAuth': idToken },
      success: function(data) {
        this.props.onUpdate("%(name)s",data);
      }.bind(this),
      error: function(xhr, status, err) {
        console.error('api/%(name)s', status, err.toString());
      }.bind(this)
    });
    this.setState({editorActive: false});
  },
  handleCancel: function() {
    this.props.onCancel(this.state.editorValues,this.props.editorMode,this.props.editorField);
    this.setState({editorActive: false});
  },""" % dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelList())

        print """
  pushInspector: function(inspector) {
    this.props.onPushInspector(inspector);    
  },
  popInspector: function(inspector) {
    this.props.onPopInspector(inspector);
  },
  render: function() {
              """
        for propertyType in objType.findall('propertyType'):
            propTypeName = ""
            if 'type' in propertyType.attrib:
                propTypeName = propertyType.get('type')
            userDefs = root.findall('objType[@name=\'%s\']' % propTypeName)
            if len(userDefs) > 0:
                userDef = userDefs[len(userDefs)-1]
                print """var %(name)sValues = %(type)sSelectorSource();""" % dict(name=propertyType.get('name'),type=userDef.get('name'))

        print """
    return (
        <Dialog
          actions={this.state.actions}
          active={this.state.editorActive}
          onEscKeyDown={this.handleCancel}
          onOverlayClick={this.handleCancel}
          title=""
        >
          <h1>{this.props.editorMode} %(label)s</h1>
          <form>
          """ % dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelList())
        for propertyType in objType.findall('propertyType'):
            propertyWrapper = PropertyWrapper(root,propertyType)
            propertyWrapper.emitFormElement()
        print """
          </form>
        </Dialog>
    );
  }
});
        """ % objType.attrib

        # objType Editor class
        print """
var %(name)sEditor = React.createClass({
  getInitialState: function() {
    return { inspectorStack:[],
        """ % objType.attrib
        print """
      };
  },
  beginAdd: function() {
    var inspector = { editorType: '%(name)s', editorMode: "ADD", editorField: "", onPushInspector: this.pushInspector, onPopInspector: this.popInspector};
    this.pushInspector(inspector);
  },
  beginEdit: function() {
    if(!this.props.hasSelected()) {
      alert("No %(label)s is selected");
    } else {
      var initialValues = this.props.getSelected();
      var inspector = { editorType: '%(name)s', editorMode: "EDIT", editorField: "", id: initialValues.id,onPushInspector: this.pushInspector, onPopInspector: this.popInspector};
      this.pushInspector(inspector);
    }
  },
  beginDelete: function() {
    if(!this.props.hasSelected()) {
      alert("No %(label)s is selected");
    } else {
      var initialValues = this.props.getSelected();
      var inspector = { editorType: '%(name)s', editorMode: "DELETE", editorField: "", id: initialValues.id,onPushInspector: this.pushInspector, onPopInspector: this.popInspector};
      this.pushInspector(inspector);
    }
  },
  pushInspector: function(inspector) {
      """  % dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelList())
        print """
    this.setState({inspectorStack: this.state.inspectorStack.concat([inspector]) });
  },
  popInspector: function() {
    this.setState({inspectorStack: this.state.inspectorStack.slice(0,-1) });
  },
  handleUpdate: function(typeName,data) {
    this.props.onUpdate(typeName,data);
    this.popInspector();
  },
  handleCancel: function(editorValues,editorMode) {
    this.popInspector();
  },

              """ % dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelList())

        print """
  render: function() {
    var nodes = [];

    if(this.state.inspectorStack.length > 0) {
      var items = [this.state.inspectorStack[this.state.inspectorStack.length-1]];
      nodes = items.map(renderItem,this);
    }

    return (
      <div className="%(name)sEditor">
        <Button label='Add' onClick={this.beginAdd} disabled={!auth.loggedIn()} />
        <Button label='Edit' onClick={this.beginEdit} disabled={!auth.loggedIn()}/>
        <Button label='Delete' onClick={this.beginDelete} disabled={!auth.loggedIn()}/>
        {nodes[0]}
      </div>
    );
  }
});
              """ %  dict(name=objType.get('name'),label=NodeWrapper(root,objType).getLabelList())

    print """
ReactDOM.render(
  <%(name)sApp pollInterval={5000}/>,
  document.getElementById('content')
);
    """ % root.attrib
  argi += 1
