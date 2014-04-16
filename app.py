#!/usr/bin/env python

from flask import Flask, request, session, redirect, url_for, flash
from flask import render_template_string
from flask.ext.github import GitHub, GitHubError

try:
    from config import SECRET_KEY, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, GITHUB_CALLBACK_URL
except ImportError:
    print ("Couldn't get data from the config.py file")
    print ("Create 'config.py' that sets 'SECREY_KEY', 'GITHUB_CLIENT_ID'," \
           "'GITHUB_CLIENT_SECRET', and 'GITHUB_CALLBACK_URL'")
    raise

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

github = GitHub(app)

HTMLBLOB = """
<!DOCTYPE HTML>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <meta name="description" content="Github Issue to Pull Request converter">
    <meta name="keywords" content="git, github, issue, pull pequest, convert">
    <meta name="viewport" content="width=device-width">
    <title>GH-I2P</title>
    <style type="text/css">
    body {
      color: #000000;
      background-color: #FFFFFF;
      text-decoration: none;
      font-family: 'arial', 'sans-serif';
    }
    main {
      text-align: center;
      margin-top: 100px;
    }
    a#title{
      color: #000000;
      text-decoration: none;
    }
    img#gh-banner {
      position: absolute;
      top: 0;
      right: 0;
      border: 0;
    }
    div.flash {
      border-radius: 10px;
      -webkit-border-radius: 10px;
      padding: 15px;
      margin: 10px auto 10px auto;
      border: 1px solid;
      max-width: 300px;
      width: 80%
    }
    div.error {
      background-color: #F2DEDE;
      border-color: #EBCCD1;
      color: #A94442;
    }
    div.message {
      background-color:#DFF0D8;
      border-color: #D6E9C6;
      color: #3C763D;
    }
    footer {
      position: absolute;
      bottom: 50px;
      right: 50px;
    }
    </style>
  </head>
  <body>
    <main>
      <a href="/" id='title'><h1>GitHub - Issue2Pull</h1></a>
      <a href="https://github.com/pR0Ps/gh-i2p"><img id="gh-banner" src="https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png" alt="Fork me on GitHub"></a>
      <p>This service allows you to easily convert a GitHub issue to a pull request.</p>
      {% with messages = get_flashed_messages(with_categories=True) %}
        {% if messages %}
          {% for c, m in messages %}
            <div class="flash {{ c }}">{{ m }}</div>
          {% endfor %}
        {% endif %}
      {% endwith %}
      {% if session['github_access_token'] %}
        <p>Signed in as {{ session['username'] }} (<a href="logout">logout</a>)</p>
        <form action="convert" method="post">
          <label for="repo">Repository:</label>
          <input type="text" id="repo" name="repo" placeholder="ex. pR0Ps/gh-i2p"/>

          <label for="issue">Issue:</label>
          <input type="number" id="issue" name="issue" value="1" min="1"/>

          <label for="head">Head:</label>
          <input type="text" id="head" name="head" placeholder="ex. [user:]bugfix"/>

          <label for="base">Master:</label>
          <input type="text" id="base" name="base" placeholder="ex. master"/>

          <input type="submit" id="submit" value="Convert"/>
        </form>
      {% else %}
        <form id="login" action="login" method="get">
          <input type="submit" value="Log in with GitHub"/>
        </form>
      {% endif %}
    </main>
    <footer>Made by <a href="http://cmetcalfe.ca">Carey Metcalfe</a></footer>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTMLBLOB)

@app.route("/login")
def login():
    if session.get('github_access_token', None) is None:
        return github.authorize(scope="repo")
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('github_access_token', None)
    return redirect(url_for('index'))

@app.route('/convert', methods=['POST'])
def convert():
    url = request.form.get('repo', None)
    params = {x: request.form.get(x, None) for x in ('issue', 'head', 'base')}
    if url is None or None in params.values():
        flash("Invalid request", "error")
        return redirect(url_for("index"))

    try:
        github.post("repos/{0}/pulls".format(url), data=params)
        flash("Pull request created!")
    except GitHubError as e:
        flash("Error from GitHub: {}".format(str(e)), 'error')
    return redirect(url_for("index"))

@github.access_token_getter
def token_getter():
    return session.get('github_access_token', None)

@app.route('/auth')
@github.authorized_handler
def auth(oauth_token):
    """Callback URL for the GitHub API"""
    next_url = request.args.get('next') or url_for('index')
    if oauth_token is None:
        flash("Authorization failed.", "error")
        return redirect(next_url)

    session['github_access_token'] = oauth_token

    try:
        data = github.get('user')
        session['username'] = data['login']
    except EnvironmentError as e:
        flash("Couldn't get user data: {0}".format(str(e)), "error")

    return redirect(next_url)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
