import requests

#api references: https://www.themealdb.com/api.php
url = "http://www.themealdb.com/api/json/v1/1/filter.php?i=chicken"

response = requests.request("GET", url)

#print(response.text)

#api references: https://rapidapi.com/spoonacular/api/recipe-food-nutrition/

url = "https://api.spoonacular.com/food/products/search?query=yogurt&apiKey="

apikey = "a8fbdd86a4e74f5897ab358e550cc549"

response2 = requests.request("GET", url+apikey)

print(response2.text)
