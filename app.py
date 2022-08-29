from email.mime import image
from importlib.metadata import files
import os
import json
from webbrowser import get
import bcrypt
from re import template
from typing import Collection
from unittest import result
from flask import (Flask, flash, render_template, redirect, request, url_for, jsonify, session)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
if os.path.exists("env.py"):
    import env

UPLOAD_FOLDER = 'static/assets/img'
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key  = os.environ.get("SECRET_KEY")
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

mongo = PyMongo(app)
recipes = mongo.db.Recipes
users = mongo.db.Users

def allowed_file(filename):
 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=['post', 'get'])
def index():
    
    message = ''
    if "email" in session:
        email = session["email"]
        name = users.find_one({"email": email}).get("name")
        return render_template('index.html', name=name)
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
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

@app.route("/addrecipe")
def addrecipe():
    if "email" in session:
        email = session["email"]
        name = users.find_one({"email": email}).get("name")
    return render_template("addrecipe.html", name=name)

@app.route('/insert_recipe', methods=['POST'])
def insert_recipe():
    if "email" in session:
        email = session["email"]
        name = users.find_one({"email": email}).get("name")
    
    file = request.files['image']
    filename = secure_filename(file.filename)
    if file and allowed_file(file.filename):
       file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    recipes.insert_one({
        'recipe_name': request.form.get('recipeName1').upper(),
        'creator': name,
        'ingredients': request.form.get('ingredients1').upper(),
        'method': request.form.get('method1').upper(),
        'image': file.filename
    })
    
    return redirect(url_for("index"))

@app.route('/delete_recipe/<recipe_id>')
def delete_recipe(recipe_id):
    recipes.remove({'_id': ObjectId(recipe_id)})
    return redirect(url_for('index'))

@app.route('/editrecipe/<recipe_id>')
def edit_recipe(recipe_id):
    if "email" in session:
        email = session["email"]
        name = users.find_one({"email": email}).get("name")
    the_recipe = recipes.find_one({"_id": ObjectId(recipe_id)})
    return render_template('editrecipe.html',
                           recipes=the_recipe, name=name)

@app.route('/update_recipe/<recipe_id>', methods=["POST"])
def update_recipe(recipe_id):
    if "email" in session:
        email = session["email"]
        name = users.find_one({"email": email}).get("name")
    
    file1 = request.files['image1']
    filename1 = secure_filename(file1.filename)
    if file1 and allowed_file(file1.filename):
        file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    recipes.update({'_id': ObjectId(recipe_id)},
                   {"$set": {
        'recipe_name': request.form.get('recipeName').upper(),
        'creator': name,
        'ingredients': request.form.get('ingredients').upper(),
        'method': request.form.get('method').upper(),
        'image': file1.filename
    }})
    return redirect(url_for('index')) 

@app.route('/search', methods=['GET'])
def search():
    results = mongo.db.Recipes.find({'recipe_name' : {'$regex' : request.values.get('recipe-search').upper()}})
    print(results)
    return render_template('searchresults.html', recipes = results)

@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    if "email" in session:
        email = session["email"]
        name = users.find_one({"email": email}).get("name")
        return render_template('index.html', name=name)

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

       
        email_found = users.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            
            if password == passwordcheck:
                session["email"] = email_val
                session['logged_in'] = True
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

    
@app.route("/logout", methods=["POST", "GET"])
def logout():
    if "email" in session:
        session.pop("email", None)
        session['logged_in'] = False
        return render_template("login.html")
    else:
        return render_template('index.html')
    
@app.route("/myRecipes")
def myRecipes():
    if "email" in session:
        email = session["email"]
        name = users.find_one({"email": email}).get("name")
    
    myrecipes = mongo.db.Recipes.find({'creator' : name})
    
    if myrecipes is not None:
        return render_template("myrecipes.html", recipes = myrecipes)