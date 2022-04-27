import os
from flask import (Flask, flash, render_template, redirect, request, url_for)
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

@app.route("/")
def home():
    recipes = mongo.db.Recipes.find()
    return render_template("index.html", recipes = recipes)

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