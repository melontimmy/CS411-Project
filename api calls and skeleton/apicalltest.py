import requests

#https://www.themealdb.com/api.php
url = "http://www.themealdb.com/api/json/v1/1/filter.php?i=chicken"

response = requests.request("GET", url)

print(response.text)

