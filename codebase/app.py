import flask
from flask import Flask, Response, request, render_template, redirect, url_for, session
from flaskext.mysql import MySQL
import flask_login
import requests
import json
import os
from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = 'secret_key'

mysql = MySQL(app)
oauth = OAuth(app)

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'mysql460' # change to your mysql pass
app.config['MYSQL_DATABASE_DB'] = 'Wattocook'


#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
conn = mysql.connect() 

def getUsers():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()


@login_manager.user_loader
def user_loader(email):
	users = getUsers()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUsers()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

####### LOGIN METHODS #########

def emailExists(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return True
	else:
		return False

class User(flask_login.UserMixin):
	pass

def loginUser(email):
	user = User()
	user.id = email
	flask_login.login_user(user) 

@app.route('/login', methods=['GET', 'POST'])
def std_login(): #standard login without oauth
	# if POST, get email and pass
	if flask.request.method == 'POST' and 'email' in request.form and 'password' in request.form:
		email = flask.request.form['email']
		if emailExists(email):
			# execute cursor to grab all fields for the user
			cursor = conn.cursor()
			cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
			data = cursor.fetchall() 
			password = str(data[0][0]) 
			if flask.request.form['password'] == password:
				loginUser(email)
				return flask.redirect(flask.url_for('loadProfile'))
		# user or pass was incorrect
		return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"
	else:
		return render_template('login.html')
	
@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('home.html', message='Logged out')
		

@app.route('/profile')
@flask_login.login_required
def loadProfile():
	email = flask_login.current_user.id
	message = 'Hi ' + email + ', here is your profile!'
	return render_template('profile.html', name=flask_login.current_user.id, message=message)

@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		phonenum=request.form.get('phonenum')
		dob=request.form.get('dob')
		fname=request.form.get('fname')
		lname=request.form.get('lname')
	except:
		return flask.redirect(flask.url_for('register'))
	
	if not emailExists(email):
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Users (email, password, phone_number, dob, first_name, last_name) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(email, password, phonenum, dob, fname, lname))
		# still need to add field for username
		conn.commit()
		loginUser(email)
		message = 'Hi ' + email + ', here is your profile!'
		return render_template('profile.html', name=flask_login.current_user.id, message=message)
	else:
		return render_template('register.html', message='Email already in use!')


###### OAUTH METHODS ########
# to test oauth gmail must be registered as a test account for this project
# cannot save google query results to database (restrictions i think), results are purged once app quits

google = oauth.register( 
	'google',
	client_id='862135099082-a6oqavdq547skp16ndpcjvvg9r9e09b5.apps.googleusercontent.com',
    client_secret='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',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)

@app.route('/google-login')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
	google = oauth.create_client('google')
	token = google.authorize_access_token()
	userinfo = token['userinfo']
	session['user'] = userinfo
	email = userinfo['email']
	if not emailExists(email): #inputs email and name into database so user can log into flask
		fname = userinfo['given_name']
		lname = userinfo['family_name']
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Users (email, first_name, last_name) VALUES ('{0}', '{1}', '{2}')".format(email, fname, lname))
	loginUser(email)
	return flask.redirect(flask.url_for('loadProfile'))

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

#default page
@app.route("/", methods=['GET'])
def homepage():
	if flask_login.current_user.is_authenticated:
		email = flask_login.current_user.id
		return render_template('home.html', message='Welcome, '+email, name=email)
	else:
		return render_template('home.html', message='Login to save your recipes')

@app.route("/", methods=['GET', 'POST'])
def home():
	if flask.request.method == 'GET':
		flask.redirect(flask.url_for('homepage'))

	else:
		ingredients = flask.request.form['includeIngredients']

		url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"

		querystring = {
			"query":"pasta",
			"cuisine":"italian",
			"diet":"vegetarian",
			"intolerances":"gluten",
			"equipment":"pan",
			"includeIngredients":ingredients,
			"excludeIngredients":"eggs",
			"addRecipeInformation":"true",
			#"titleMatch":"Crock Pot",
			"ignorePantry":"true",

			"sort":"calories",
			"sortDirection":"asc",

			"offset":"0",
			"number":"20",
			"limitLicense":"false",

			"instructionsRequired":"true",
			"fillIngredients":"true"
			#should include ranking, should be a radio button
			}

		headers = {
			"X-RapidAPI-Key": "7912aaf695msh41bcbd54212220dp1fe4b0jsn348ff00d1c37",
			"X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
		}

		response = requests.request("GET", url, headers=headers, params=querystring).json()["results"]

		print(response)

		return render_template('home.html', recipes = response, lastquery=querystring) 

if __name__ == "__main__": app.run(port=5000, debug=True)

