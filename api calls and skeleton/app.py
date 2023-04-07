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

		query = {'includeIngredients':ingredients, 'apiKey':'a8fbdd86a4e74f5897ab358e550cc549'}
		response = requests.get('https://api.spoonacular.com/recipes/complexSearch', params=query).json()["results"]

		print(response)

		return render_template('home.html', recipes = response)

if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)