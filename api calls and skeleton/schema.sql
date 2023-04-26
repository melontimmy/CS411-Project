CREATE DATABASE IF NOT EXISTS Wattocook;
show databases;
use Wattocook;

CREATE TABLE IF NOT EXISTS Users (
    user_id int4 AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE,
    phone_number INT,
    password VARCHAR(255),
	dob DATE,
    first_name CHAR(27),
    last_name CHAR(27),
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS Food_categories(
	category_id int4 AUTO_INCREMENT, 
    category_name VARCHAR(255),
    CONSTRAINT categories_pk PRIMARY KEY (category_id)

);

CREATE TABLE IF NOT EXISTS Cuisines(
	cuisine_id int4 AUTO_INCREMENT, 
    cuisine_name VARCHAR(255),
    CONSTRAINT cuisines_pk PRIMARY KEY (cuisine_id)

);

CREATE TABLE IF NOT EXISTS Ingredients( 
	ingredient_id int4 AUTO_INCREMENT, 
    ingredient_name VARCHAR(255),
    date_added DATE,
    category_id int4,
    CONSTRAINT ingredients_pk PRIMARY KEY (ingredient_id),
    FOREIGN KEY (category_id) REFERENCES Food_categories(category_id) ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS Recipes( 
	recipe_id int4 AUTO_INCREMENT, 
    recipe_name VARCHAR(255),
    date_saved DATE,
    cooked BIT,
    cuisine_id int4,
    CONSTRAINT recipes_pk PRIMARY KEY (recipe_id),
    FOREIGN KEY (cuisine_id) REFERENCES Cuisines(cuisine_id) ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS Saved_by(
	user_id int4,
    recipe_id int4,
    PRIMARY KEY (user_id, recipe_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (recipe_id) REFERENCES Recipes(recipe_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Owned_by(
	user_id int4,
    ingredient_id int4,
    PRIMARY KEY (user_id, ingredient_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Recipe_contains(
	recipe_id int4,
    ingredient_id int4,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES Recipes(recipe_id),
    FOREIGN KEY (ingredient_id) REFERENCES Ingredients(ingredient_id)
);
