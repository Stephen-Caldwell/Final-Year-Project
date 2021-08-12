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
    return render_template("index.html")

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
        'chef name': request.form.get('chefName1'),
        'ingredients1': request.form.get('ingredients1'),
        'method1': request.form.get('method1')
    })
    return redirect(url_for('/addrecipe'))


# @app.route("/editrecipe", methods=["GET", "POST"])
# def addrecipe():
#     return render_template("addrecipe.html")

# @app.route("/addrecipe", methods=["GET", "POST"])
# def addrecipe():
#     return render_template("addrecipe.html")