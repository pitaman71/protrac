const React = require('react');
const ReactDOM = require('react-dom');
const toolbox = require('react-toolbox');
const Tabs = toolbox.Tabs;
const Tab = toolbox.Tab;
const Dropdown = toolbox.Dropdown;

class ProgressTrackingApp extends React.Component {
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

  render() {
    return (
      <div>
        <h1>Beta School Progress Tracking</h1>
        <Tabs index={this.state.index} onChange={this.handleTabChange}>
          <Tab label="People">
            <PeopleBox url="/api/people" pollInterval={2000} />
          </Tab>
          <Tab label="Progress">
            <ProgressBox url="/api/progress" pollInterval={2000} />
          </Tab>
          <Tab label="Comments">
            <CommentBox url="/api/comments" pollInterval={2000} />
          </Tab>
        </Tabs>
        </div>
    );
  }
}

var Person = React.createClass({
  render: function() {
    var md = new Remarkable();
    return (
      <tr className="person">
        <td>{this.props.given}</td>
        <td>{this.props.surname}</td>
      </tr>
    );
  }
});

var PeopleList = React.createClass({
  render: function() {
    var peopleNodes = this.props.data.map(function(person) {
      return (
        <Person surname={person.surname} given={person.given} key={person.id}/>
      );
    });
    return (
      <div className="peopleList">
      <table>
        <tbody>
        {peopleNodes}
        </tbody>
      </table>
      </div>
    );
  }
});
var PeopleBox = React.createClass({
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
  },
  handleCommentSubmit: function(comment) {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'POST',
      data: comment,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    this.loadFromServer();
    setInterval(this.loadFromServer, this.props.pollInterval);
  },
  render: function() {
    return (
      <div className="peopleBox">
        <h1>People</h1>
        <PeopleList data={this.state.data} />
      </div>
    );
  }
});

var Comment = React.createClass({
  rawMarkup: function() {
    var md = new Remarkable();
    var rawMarkup = md.render(this.props.children.toString());
    return { __html: rawMarkup };
  },

  render: function() {
    var md = new Remarkable();
    return (
      <div className="comment">
        <h2 className="commentAuthor">
          {this.props.author}
        </h2>
        <span dangerouslySetInnerHTML={this.rawMarkup()} />
      </div>
    );
  }
});
var CommentList = React.createClass({
  render: function() {
    var commentNodes = this.props.data.map(function(comment) {
      return (
        <Comment author={comment.author} key={comment.id}>
          {comment.text}
        </Comment>
      );
    });
    return (
      <div className="commentList">
        {commentNodes}
      </div>
    );
  }
});

var CommentForm = React.createClass({
  getInitialState: function() {
    return {author: '', text: ''};
  },
  handleAuthorChange: function(e) {
    this.setState({author: e.target.value});
  },
  handleTextChange: function(e) {
    this.setState({text: e.target.value});
  },
  handleSubmit: function(e) {
    e.preventDefault();
    var author = this.state.author.trim();
    var text = this.state.text.trim();
    if (!text || !author) {
      return;
    }
    // TODO: send request to the server
    this.props.onCommentSubmit({author: author, text: text});
    this.setState({author: '', text: ''});
  },
  render: function() {
    return (
      <form className="commentForm" onSubmit={this.handleSubmit}>
        <input
          type="text"
          placeholder="Your name"
          value={this.state.author}
          onChange={this.handleAuthorChange}
        />
        <input
          type="text"
          placeholder="Say something..."
          value={this.state.text}
          onChange={this.handleTextChange}
        />
        <input type="submit" value="Post" />
      </form>
    );
  }
});
var CommentBox = React.createClass({
  loadCommentsFromServer: function() {
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
  },
  handleCommentSubmit: function(comment) {
    $.ajax({
      url: this.props.url,
      dataType: 'json',
      type: 'POST',
      data: comment,
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    this.loadCommentsFromServer();
    setInterval(this.loadCommentsFromServer, this.props.pollInterval);
  },
  render: function() {
    return (
      <div className="commentBox">
        <h1>Comments</h1>
        <CommentList data={this.state.data} />
        <CommentForm onCommentSubmit={this.handleCommentSubmit} />
      </div>
    );
  }
});

const ProgressValues = [
  { value: '2', label: 'Super' },
  { value: '1', label: 'Very Good'},
  { value: '0', label: 'Good'},
  { value: '-1', label: 'Needs Improvement' },
  { value: '-2', label: 'Unsatisfactory'}
];


var Progress = React.createClass({
  studentValues: [
    {
        "label": "Pita, Allyson",
        "value": 1
    },
    {
        "label": "Barnes, Yasmin",
        "value": 2
    }
  ],
  render: function() {
    var md = new Remarkable();
    var student = this.studentValues.find(function(row) { return row.value == this.props.idPerson; }.bind(this));
    var effort = ProgressValues.find(function(row) { return row.value == this.props.effort; }.bind(this));
    var achievement = ProgressValues.find(function(row) { return row.value == this.props.achievement; }.bind(this));
    var cooperation = ProgressValues.find(function(row) { return row.value == this.props.cooperation; }.bind(this));
    return (
      <tr className="progress">
        <td>{student.label}</td>
        <td>{effort.label}</td>
        <td>{achievement.label}</td>
        <td>{cooperation.label}</td>
      </tr>
    );
  }
});
var ProgressList = React.createClass({
  render: function() {
    var nodes = this.props.data.map(function(row) {
      return (
        <Progress idPerson={row.idPerson} effort={row.effort} achievement={row.achievement} cooperation={row.cooperation} key={row.id}/>
      );
    });
    return (
      <div className="progressList">
      <table>
        <tbody>
        {nodes}
        </tbody>
      </table>
      </div>
    );
  }
});

var ProgressForm = React.createClass({
  studentValues: [
    {
        "label": "Pita, Allyson",
        "value": 1
    },
    {
        "label": "Barnes, Yasmin",
        "value": 2
    }
  ],
  getInitialState: function() {
    return {author: '', text: ''};
  },
  handleStudentChange: function(value) {
    this.setState({idPerson: value});
  },
  handleEffortChange: function(value) {
    this.setState({effort: value});
  },
  handleAchievementChange: function(value) {
    this.setState({achievement: value});
  },
  handleCooperationChange: function(value) {
    this.setState({cooperation: value});
  },
  handleSubmit: function(e) {
    e.preventDefault();
    var idPerson = this.state.idPerson;
    var effort = this.state.effort;
    var achievement = this.state.achievement;
    var cooperation = this.state.cooperation;    
    if (!idPerson || !effort || !achievement || !cooperation) {
      return;
    }
    // TODO: send request to the server
    this.props.onSubmit({idPerson: idPerson, effort: effort, achievement: achievement, cooperation: cooperation});
    this.setState({author: '', text: ''});
  },
  render: function() {
    return (
      <form className="progressForm" onSubmit={this.handleSubmit}>
        <Dropdown
          auto
          onChange={this.handleStudentChange}
          source={this.studentValues}
          value={this.state.idPerson}
          label="Weekly Report for Student:"
        />
        <Dropdown
          auto
          onChange={this.handleEffortChange}
          source={ProgressValues}
          value={this.state.effort}
          label="Effort:"
        />
        <Dropdown
          auto
          onChange={this.handleAchievementChange}
          source={ProgressValues}
          value={this.state.achievement}
          label="Achievement:"
        />
        <Dropdown
          auto
          onChange={this.handleCooperationChange}
          source={ProgressValues}
          value={this.state.cooperation}
          label="Cooperation:"
        />
        <input type="submit" value="Post" />
      </form>
    );
  }
});
var ProgressBox = React.createClass({
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
    return {data: []};
  },
  componentDidMount: function() {
    this.loadFromServer();
    setInterval(this.loadFromServer, this.props.pollInterval);
  },
  render: function() {
    return (
      <div className="progressBox">
        <h1>Weekly Progress Reports</h1>
        <ProgressList data={this.state.data} />
        <h1>add Progress Report</h1>
        <ProgressForm onSubmit={this.handleSubmit} />
      </div>
    );
  }
});

ReactDOM.render(
  <ProgressTrackingApp/>,
  document.getElementById('content')
);
