#!/usr/bin/env python

from bottle import Bottle, route, run, request, redirect

try:
    from config import GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
except ImportError:
    print ("Couldn't get the GitHub API tokens")
    print ("Create a script 'config.py' that sets 'GITHUB_CLIENT_ID' and 'GITHUB_CLIENT_SECRET'")
    raise

app = application = Bottle()

HTMLBLOB = """
<!DOCTYPE HTML>
<html>
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
    <meta name="description" content="Github Issue to Pull Request converter">
    <meta name="keywords" content="git, github, issue, pull pequest, convert">
    <title>GH-I2P</title>
    <style type="text/css">
    body {{
      color: #000000;
      background-color: #FFFFFF;
      text-decoration: none;
      font-family: 'arial', 'sans-serif';
    }}
    main {{
      text-align: center;
      margin-top: 100px;
    }}
    a#title{{
      color: #000000;
      text-decoration: none;
    }}
    img#gh-banner {{
      position: absolute;
      top: 0;
      right: 0;
      border: 0;
    }}
    footer {{
      position: absolute;
      bottom: 50px;
      right: 50px;
    }}
    </style>
  </head>
  <body>
    <main>
      <a href="/" id='title'><h1>Github - Issue2Pull</h1></a>
      <a href="https://github.com/pR0Ps/gh-i2p"><img id="gh-banner" src="https://s3.amazonaws.com/github/ribbons/forkme_right_darkblue_121621.png" alt="Fork me on GitHub"></a>
    </main>
    <footer>Made by <a href="http://cmetcalfe.ca">Carey Metcalfe</a></footer>
</html>"""

@app.route('/')
def index():
    return HTMLBLOB.format()

@app.route("/auth")
def auth():
    """Callback URL for the GitHub API"""
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
