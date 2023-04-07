#Borrowed from CS460, further edits pending

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import requests
import json
from requests.auth import HTTPBasicAuth

app = Flask(__name__)


#begin code used for login

class User(flask_login.UserMixin):
	pass

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


#default page
@app.route("/", methods=['GET', 'POST'])
def home():
	if flask.request.method == 'GET':
		return render_template('home.html', message='Welcome to Wattocook')
	else:
		ingredients = flask.request.form['ingredients']

		url = "https://api.spoonacular.com/food/products/search?query=yogurt&apiKey="
		apikey = "a8fbdd86a4e74f5897ab358e550cc549"
		
		auth = HTTPBasicAuth('apikey', "a8fbdd86a4e74f5897ab358e550cc549")

		#query = {'includeIngredients':ingredients}
		#response = requests.get('https://api.spoonacular.com/recipes/complexSearch', params=query, auth=auth)

		response2 = requests.request("GET", url+apikey).json()["products"]


		return render_template('home.html', recipes = response2)

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)