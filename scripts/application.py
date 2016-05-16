from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)

engine = create_engine("postgresql://ddominguez:u8paz3500k@aa1n9lvw4037g4u.cgtfuf6sekto.us-west-2.rds.amazonaws.com:5432/twitterpoll_db")
conn = engine.connect()
# print(conn)

result = conn.execute("SELECT * FROM CANDIDATES")
# result = conn.execute("SELECT COUNT(TWEET_ID) FROM TWEETS WHERE cand_id = ")
for row in result:
    print(row)
conn.close()

# print a nice greeting.
def say_hello(username = "World"):
    return '<p>Hello %s!</p>\n' % username

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

# add a rule for the index page.
application.add_url_rule('/', 'index', (lambda: header_text +
    say_hello() + instructions + footer_text))

# add a rule when the page is accessed with a name appended to the site
# URL.
application.add_url_rule('/<username>', 'hello', (lambda username:
    header_text + say_hello(username) + home_link + footer_text))

# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()
