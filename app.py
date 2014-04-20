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
      display: inline-block;
      text-align: left;
      border-radius: 10px;
      -webkit-border-radius: 10px;
      padding: 15px;
      margin: 10px auto 10px auto;
      border: 1px solid;
      max-width: 570px;
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
    form:not(#login) {
      width: 300px;
      margin: 0px auto;
      text-align: left;
    }
    table {
      width: 300px;
    }
    td.label {
      width: 110px;
    }
    input {
      padding: 5px 15px;
      margin: 1px 1px;
      border-radius: 5px;
      -webkit-border-radius: 5px;
      border: 2px solid;
    }
    input[type=submit] {
      cursor:pointer;
      font-weight: bold;
      background: #C0C0C0;
      margin-top: 10px
    }
    input#issue {
      width: 45px;
    }
    footer {
      padding: 25px;
      text-align: center;
    }
    </style>
  </head>
  <body>
    <main>
      <a href="/" id='title'><h1>GitHub - Issue2Pull</h1></a>
      <a href="https://github.com/pR0Ps/gh-i2p"><img id="gh-banner" src="https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png" alt="Fork me on GitHub"></a>
      <p>This service allows you to easily convert a GitHub issue to a pull request.</p>
      {% for c in ('message', 'error') %}
        {% with messages = get_flashed_messages(category_filter=[c]) %}
          {% if messages %}
            <div class="flash {{ c }}">
            {{ messages[0] }}
            {% if messages|length > 1 %}
              <ul>
              {% for m in messages[1:] %}
                <li>{{ m }}</li>
              {% endfor %}
              </ul>
            {% endif %}
            </div><br/>
          {% endif %}
        {% endwith %}
      {% endfor %}
      {% if session['github_access_token'] %}
        <p>Signed in as {{ session['username'] }} (<a href="logout">logout</a>)</p>
        <form action="convert" method="post">
          <table><tbody>
            <tr>
              <td class="label"><label for="repo">Repository:</label></td>
              <td class="input"><input type="text" id="repo" name="repo" value="{{ request.args.get('repo', '') }}" placeholder="ex. pR0Ps/gh-i2p"/></td>
            </tr>
            <tr>
              <td><label for="issue">Issue:</label></td>
              <td><input type="number" id="issue" name="issue" value="{{ request.args.get('issue', '1')}}" min="1"/></td>
            </tr>
            <tr>
              <td><label for="head">Head:</label></td>
              <td><input type="text" id="head" name="head" value="{{ request.args.get('head', '') }}" placeholder="ex. [user:]bugfix"/></td>
            </tr>
            <tr>
              <td><label for="base">Base:</label></td>
              <td><input type="text" id="base" name="base" value="{{ request.args.get('base', '') }}" placeholder="ex. master"/></td>
            </tr>
            <tr>
              <td></td>
              <td><input type="submit" id="submit" value="Convert"/></td>
            </tr>
          </tbody></table>
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

    error_page = url_for("index", repo=url, **params)

    if any(not x for x in params.values()) or not url:
        flash("Invalid request: All fields are required", "error")
        return redirect(error_page)

    try:
        r = github.post("repos/{0}/pulls".format(url), data=params)
        url = r.get("html_url", None)
        if url:
            flash("Pull request created! See it <a href='{}'>here</a>.".format(url))
        else:
            flash("Pull request created!")

        return redirect(url_for("index"))

    except AssertionError as e:
        # The GitHub-Flask library asserts false when GitHub
        # returns anything other than a 4xx or a 2xx code
        flash("Error from GitHub: Unknown Error")
    except GitHubError as e:
        # If there is more than 1 flash, the first will be the 'title'
        # and the rest details.
        flash("Error from GitHub: '{}'".format(str(e)), 'error')
        for err in e.response.json().get("errors", []):
            msg = err.get("message", "")
            value = err.get("value", "")

            # Field and code should always be sent, but sometimes aren't. Being safe here.
            # Ex. No field retured when trying to make a pull request that already exists.
            field = err.get("field", "")
            code = err.get("code", "")

            if msg:
                # Most human-readable
                flash(msg, 'error')
            elif code == "invalid":
                if value:
                    flash ("Invalid value '{0}' for {1}".format(value, field), 'error')
                else:
                    flash ("Invalid value for {0}".format(field), 'error')
            else:
                flash ("Returned a code '{0}' for field '{1}'".format(code, field), 'error')

    return redirect(error_page)

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
