CREATE DATABASE IF NOT EXISTS Wattocook;
show databases;
use Wattocook;

CREATE TABLE IF NOT EXISTS Users (
    user_id int4 AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE,
    phone_number INT,
    password VARCHAR(255),
	dob DATE,
    first_name CHAR(27),
    last_name CHAR(27),
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE IF NOT EXISTS Ingredients( 
	ingredient_id int4 AUTO_INCREMENT, 
    ingredient_name VARCHAR(255),
    date_added DATE,
    CONSTRAINT ingredients_pk PRIMARY KEY (ingredient_id),
);

CREATE TABLE IF NOT EXISTS Recipes( 
	recipe_id int4 AUTO_INCREMENT, 
    recipe_name VARCHAR(255),
    date_saved DATE,
    CONSTRAINT recipes_pk PRIMARY KEY (recipe_id),
);

CREATE TABLE IF NOT EXISTS Saved_by(
	user_id int4,
    recipe_id int4,
    cooked BIT,
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
