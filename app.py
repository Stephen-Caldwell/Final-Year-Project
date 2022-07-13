import os
import json
import bcrypt
from re import template
from typing import Collection
from unittest import result
from flask import (Flask, flash, render_template, redirect, request, url_for, jsonify, session)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key  = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)
recipes = mongo.db.Recipes
users = mongo.db.Users

@app.route("/", methods=['post', 'get'])
def index():
    message = ''
    if "email" in session:
        return render_template('index.html')
    if request.method == "POST":
        user = request.form.get("name")
        email = request.form.get("email")
        
        password1 = request.form.get("password")
        password2 = request.form.get("confirm_password")
        
        email_found = users.find_one({"email": email})
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('register.html', message=message)
        else:
            hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
            user_input = {'name': user, 'email': email, 'password': hashed}
            users.insert_one(user_input)
            
            user_data = users.find_one({"email": email})
            new_email = user_data['email']
   
            return render_template('index.html', email=new_email)
    return render_template('register.html')

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

@app.route("/addrecipe")
def addrecipe():
    return render_template("addrecipe.html")

@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    recipes.insert_one({
        'recipe_name': request.form.get('recipeName1'),
        'creator': request.form.get('chefName1'),
        'ingredients': request.form.get('ingredients1'),
        'method': request.form.get('method1')
    })
    return redirect(url_for("home"))

@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('home'))

@app.route('/editrecipe/<recipe_id>')
def edit_recipe(recipe_id):
    the_recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template('editrecipe.html',
                           recipes=the_recipe)

@app.route('/update_recipe/<recipe_id>', methods=["POST"])
def update_recipe(recipe_id):
    recipes.update({'_id': ObjectId(recipe_id)},
                   {
        'recipe_name': request.form.get('recipeName'),
        'chef_name': request.form.get('chefName'),
        'ingredients': request.form.get('ingredients'),
        'method': request.form.get('method')
    })
    return redirect(url_for('home'))       

@app.route('/search', methods=['GET'])
def search():
        results = mongo.db.Recipes.find({}, request.form.get('search'))
        return render_template('index.html', results = results)

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        return render_template('index.html')

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

       
        email_found = users.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if password == passwordcheck:
                session["email"] = email_val
                return redirect(url_for('index'))
            else:
                if "email" in session:
                    return redirect(url_for("logged_in"))
                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/insert_user', methods=['POST'])
def insert_user():
    users.insert_one({
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'password': request.form.get('password')
    })
    return redirect(url_for("index"))