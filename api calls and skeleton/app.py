import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import requests
import json

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
		return render_template('home.html', message='UserName')
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

