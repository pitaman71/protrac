const React = require('react');
const ReactDOM = require('react-dom');
const toolbox = require('react-toolbox');
const Tabs = toolbox.Tabs;
const Tab = toolbox.Tab;

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
            Progress reports here ...
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
      <table border>
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
ReactDOM.render(
  <ProgressTrackingApp/>,
  document.getElementById('content')
);


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
ReactDOM.render(
  <ProgressTrackingApp/>,
  document.getElementById('content')
);
