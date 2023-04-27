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

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

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
	return render_template('browse.html', message='Logged out')
		

@app.route('/profile')
@flask_login.login_required
def loadProfile():
	email = flask_login.current_user.id
	message = 'Hi ' + email + ', here is your profile!'

	url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/informationBulk"

	querystring = {"ids":','.join(str(x) for x in getSavedRecipes())}

	headers = {
		"X-RapidAPI-Key": "7912aaf695msh41bcbd54212220dp1fe4b0jsn348ff00d1c37",
		"X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
	}
	response = requests.get(url, headers=headers, params=querystring).json()

	#print(response["result"])
	return render_template('profile.html', name=flask_login.current_user.id, message=message, recipes=response)

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

####### INGREDIENTS METHODS ########

def getIngredients():
	email = flask_login.current_user.id
	id = getUserIdFromEmail(email)
	cursor = conn.cursor()
	cursor.execute("SELECT ingredient_name FROM Ingredients NATURAL JOIN Owned_by WHERE user_id = '{0}'".format(id))
	ingredients = []
	if cursor.rowcount > 0:
		for i in cursor:
			ingredients.append(i[0])

	return ingredients

def ingredientExists(ingredient):
	# returns -1 if ingredient not found
	cursor = conn.cursor()
	if cursor.execute("SELECT ingredient_id FROM Ingredients WHERE ingredient_name = '{0}'".format(ingredient)):
		#this means there are greater than zero entries with that ingredient name
		return cursor.fetchone()[0]
	else:
		return -1
	
def alreadyInFridge(ingredient):
	# returns -1 if ingredient not found
	email = flask_login.current_user.id
	uid = getUserIdFromEmail(email)
	iid = ingredientExists(ingredient)
	cursor = conn.cursor()
	if cursor.execute("SELECT ingredient_id FROM Owned_by WHERE ingredient_id = '{0}' AND user_id = '{1}'".format(iid, uid)):
		#this means there are greater than zero entries with that ingredient name
		return True
	else:
		return False


@app.route('/fridge')
def fridge():
	ingredients = getIngredients()
	if len(ingredients) > 0:
		return render_template('fridge.html', ingredients=ingredients)
	return render_template('fridge.html')


@app.route("/fridge", methods=['POST', 'GET'])
@flask_login.login_required
def fridge_handler():
	cmd = request.form.get("cmd")
	if cmd == "Delete":
		return deleteFromFridge()
	else:
		return addToFridge()

@app.route('/fridge')
def addToFridge():
	try:
		ingredients = flask.request.form['ingredients']
	except:
		return flask.redirect(flask.url_for('fridge'))
	list = ingredients.split(',')

	email = flask_login.current_user.id
	uid = getUserIdFromEmail(email)
	cursor = conn.cursor()
	for i in list:
		if i != '':
			iid = ingredientExists(i)
			if iid == -1:
				# add ingredient to existing list
				cursor.execute("INSERT INTO Ingredients (ingredient_name) VALUE ('{0}')".format(i))
				conn.commit()
				iid = ingredientExists(i)
			if not alreadyInFridge(i):
				cursor.execute("INSERT INTO Owned_by (user_id, ingredient_id) VALUES ('{0}', '{1}')".format(int(uid), int(iid)))
				conn.commit()

	return flask.redirect(flask.url_for('fridge'))

@app.route("/fridge")
def deleteFromFridge():
	try:
		ingredients = flask.request.form['ingredients']
	except:
		return flask.redirect(flask.url_for('fridge'))
	list = ingredients.split(',')
	email = flask_login.current_user.id
	uid = getUserIdFromEmail(email)
	cursor = conn.cursor()
	for i in list:
		if i != '':
			iid = ingredientExists(i)
			if alreadyInFridge(i):
				cursor.execute("DELETE FROM Owned_by WHERE user_id = '{0}' AND ingredient_id = '{1}'".format(uid, iid))
				conn.commit()
	return flask.redirect(flask.url_for('fridge'))


	#default page

@app.route("/", methods=['GET', 'POST'])
def browse():
	if flask.request.method == 'GET':

		if flask.request.full_path.find("query") != -1:

			variables = ["query", "cuisine", "diet", "intolerances", "equipment", "includeIngredients", "excludeIngredients", "titleMatch", "offset", "sort", "sortDirection"]
			varDict = {}

			querystring = {
				"number":"20",
				"ignorePantry":"true",
				"addRecipeInformation":"true",
				"instructionsRequired":"true",
				"fillIngredients":"true"
				#should include ranking, should be a radio button
				}
			
			for variableName in variables:
				if request.args.get(variableName):
					querystring[variableName] = request.args.get(variableName)
					varDict[variableName] = request.args.get(variableName)
			
			headers = {
				"X-RapidAPI-Key": "7912aaf695msh41bcbd54212220dp1fe4b0jsn348ff00d1c37",
				"X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
			}

			url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/complexSearch"

			response = requests.request("GET", url, headers=headers, params=querystring)

			message = 'Login to save your recipes'
			email = None

			if flask_login.current_user.is_authenticated:
				email = flask_login.current_user.id
				message = 'Welcome, ' + email
	
			if response.status_code == 200:
				return render_template('browse.html', recipes = response.json()["results"], message=message, **varDict, name=email)
			else:
				return render_template('browse.html', message='Something went wrong! Code: ' + str(response.status_code))

		else:
	
			if flask_login.current_user.is_authenticated:
				email = flask_login.current_user.id
				return render_template('browse.html', message='Welcome, '+email, name=email)
			else:
				return render_template('browse.html', message='Login to save your recipes')
	else:
		def display(offset):
			variables = ["query", "cuisine", "diet", "intolerances", "equipment", "includeIngredients", "excludeIngredients", "titleMatch", "offset", "sort", "sortDirection"]
			varDict = {}
			for variableName in variables:
				if flask.request.form.get(variableName):
					varDict[variableName] = flask.request.form[variableName]
			
			#print(varDict)
			#varDict["query"] = varDict.get("query") if varDict.get("query") else ""
			varDict["offset"] = int(varDict.get("offset")) + offset if varDict.get("offset") else offset

			if varDict["offset"] < 0: varDict["offset"]	= 0

			return redirect(url_for('browse', **varDict))
		if flask.request.form.get('submit'):
			return display(0)
		elif flask.request.form.get("forward"):
			return display(20)
		elif flask.request.form.get("back"):
			return display(-20)
		
@app.route("/recipe/", methods=['GET', 'POST'])
def recipe():
	if flask.request.method == 'GET':
		id = request.args.get("id")
		if id:

			headers = {
				"X-RapidAPI-Key": "7912aaf695msh41bcbd54212220dp1fe4b0jsn348ff00d1c37",
				"X-RapidAPI-Host": "spoonacular-recipe-food-nutrition-v1.p.rapidapi.com"
			}

			querystring = {
				"includeNutrition" : "true"
			}

			url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/" + str(id) + "/information"
			
			response = requests.request("GET", url, headers=headers, params=querystring)

			saved = False
			
			if flask_login.current_user.is_authenticated:
				saved = recipeSaved(id)
			return render_template('recipe.html', recipe=response.json(), saved=saved, id=id)
	else:
		if not flask_login.current_user.is_authenticated:
			return flask.redirect(flask.url_for('std_login'))
		email = flask_login.current_user.id
		uid = getUserIdFromEmail(email)
		cursor = conn.cursor()
		id = request.args.get("id")
		if id:
			if recipeSaved(id):
				#remove recipe
				cursor.execute("DELETE FROM Saved_by WHERE user_id = '{0}' AND recipe_id = '{1}'".format(uid, id))
	
				conn.commit()
			else:
				if not cursor.execute("SELECT recipe_id FROM Recipes WHERE recipe_id = '{0}'".format(id)):
					cursor.execute("INSERT INTO Recipes (recipe_id) VALUES ('{0}')".format(id))
				cursor.execute("INSERT INTO Saved_by (user_id, recipe_id) VALUES ('{0}', '{1}')".format((uid), (id)))
				conn.commit()

				#add recipe
			return flask.redirect(flask.url_for('loadProfile'))


def getSavedRecipes(): 
	email = flask_login.current_user.id
	id = getUserIdFromEmail(email)
	cursor = conn.cursor()
	cursor.execute("SELECT recipe_id FROM Recipes NATURAL JOIN Saved_by WHERE user_id = '{0}'".format(id))
	recipes = []
	if cursor.rowcount > 0:
		for i in cursor:
			recipes.append(i[0])

	return recipes

def recipeSaved(recipeID):
	email = flask_login.current_user.id
	uid = getUserIdFromEmail(email)
	cursor = conn.cursor()
	if cursor.execute("SELECT recipe_id FROM Saved_by WHERE recipe_id = '{0}' AND user_id = '{1}'".format(recipeID, uid)):
		return True
	else:
		return False

	
if __name__ == "__main__": app.run(port=5000, debug=True)