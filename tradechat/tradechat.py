import os
import datetime as dt
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
					abort, render_template, flash
					
app = Flask(__name__)

app.config.update(
	dict(
		DATABASE=os.path.join(app.root_path, 'tradechat.db'),
		DEBUG=True,
		SECRET_KEY = 'secret_key'
		)
	)
	
app.config.from_envvar('TC_SETTINGS', silent=True)

def connect_db():
	#connects to the TC database
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv
	
def get_db():
	if not hasattr(g, 'sqlite_db'):
		#open only if none exists yet
		g.sqlite_db = connect_db()
	return g.sqlite_db
	
def init_db():
	with app.app_context():
		db = get_db()
		with app.open_resource('tables.sql', 'r') as f:
			db.cursor().executescript(f.read())
		db.commit()
		
@app.teardown_appcontext
def close_db(error):
	''' Closes the TC database at the end of the request. '''
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()
		
		
@app.route('/')
def show_entries():
	db = get_db()
	query = 'select comment, user, time from comments order by id desc'
	cursor = db.execute(query)
	comments = cursor.fetchall()
	return render_template('show_entries.html', comments = comments)
	
@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Registers a new user in the TC database"""
	error = None
	if request.method == 'POST':
		db.et_db()
		if request.form['username'] == "" or request.form['password'] =="":
			error = "Provide both a username and a password."
			# both fields have to be nonempty
		else:
			db.execute('insert into users (name, password) values (?, ?)',
						[request.form['username'], request.form['password']])
			db.commit()
			session['logged_in'] = True
			# directly log in user
			flash('You were successfully registered.')
			app.config.update(dict(USERNAME=request.form['username']))
			return redirect(url_for('show_entries'))
	return render_template('register.html', error=error)

@app.route('/register', methods=["GET","POST"])
def login():
	"'Logs user in'"
	error = None
	if request.method == "POST":
		db = get_db()
		try:
			query = 'select id from users where name = ? and password=?'
			id = db.execute(query, (request.form['username'], 
									request.form['password'])).fetchone()[0]
				# fails if record with provided username and password 
				# is not found
			session['logged_in'] = True
			flash('You are now logged in.')
			app.config.update(dict(USERNAME=request.form['username']))
			return redirect(url_for('show_entries'))
		except:
			error = "User not found or wrong password."
	return render_template('login.html', error=error)
	
app.route('/add', methods=['POST'])
def add_entry():
	"' Adds entry to the TC database. '"
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	now = dt.datetime.now()
	db.execute('insert into comments (comment, user, time) values (?,?,?)',
			[request.form['text'], app.config['USERNAME'], str(now)[:-7]])
	db.commit()
	flash('Your comment was successfully added.')
	return redirect(url_for('show_entries'))

app.route('/logout')
def logout():
	""" Logs out the current user. """
	session.pop('logged_in', None)
	flash('You were logged out.')
	return redirect(url_for('show_entries'))


if __name__=='__main__':
	init_db()
	
	app.run()