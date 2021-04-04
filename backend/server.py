import json
import io
from hashlib import * 
from flask import Flask, request, render_template, url_for, make_response, jsonify, send_file, session
from flask_mongoengine import MongoEngine
import mongoengine as db 
from constants import *
import requests
app = Flask(__name__)
mongodb_pass = 'MyBiLU2HPTEYnoN5'
db_name = "Main"
DB_URI = "mongodb+srv://Brian:{}@princetonunihack.rvwct.mongodb.net/{}?retryWrites=true&w=majority".format(mongodb_pass, db_name)
app.config["MONGODB_HOST"] = DB_URI
db = MongoEngine()
db.init_app(app)

app = Flask(__name__)

class User(db.Document):
    username = db.StringField()
    password = db.StringField()
    email = db.EmailField() #adding email address field to the document
    investmentstyle = db.StringField() #Choice of Value, Growth, Speculative
    investmenthorizon = db.StringField() #Choice of Day, Monthly, Annual, Long-Term
    favourites = db.DictField()
    def to_json(self): 
        return {
            "username": self.username,
            "email":self.email, #adding email address field to JSON
            "investmentstyle": self.investmentstyle, 
            "investmenthorizon": self.investmenthorizon,
            "favourites": self.favourites
        }


@app.route("/")
def mainpage():
    response = requests.get('https://sandbox.tradier.com/v1/markets/search',
        params={'q': 'alphabet', 'indexes': 'false'},
        headers={'Authorization': 'Bearer EQGhrbEgpNGAVsdNEDJ4RT0TJoBY', 'Accept': 'application/json'}
    )
    print("hello")
    #json_response = response.json()
    print(response.status_code)
    #print(json_response)
    return "bob"


#Example http://127.0.0.1:5000/register?username=bob&style=long&horizon=annual       

@app.route("/register", methods = ['POST'])
def register(): 
    user = request.form["username"]
    passw = request.form['password']
    mail = request.form["email"]
    style = request.form["style"]
    horizon = request.form["horizon"]
    favorites = request.form["favourites"]
    favlst = favorites.split(",")
    json = {'0':favlst[0], '1':favlst[1], '2':favlst[2]}
    print(json)
    if User.objects(username = user).first(): 
        return make_response("That username already exists", 400)
    else:
        newuser = User(username = user, password = sha256(passw.encode('utf-8')).hexdigest(), email = mail, investmentstyle = style, investmenthorizon = horizon, favourites = json)
        newuser.save() 
    return make_response("success", 201)

@app.route("/login", methods = ['POST'])
def login(): 
    if "user" in session: 
        return make_response("User already logged in", 400)
    else: 
        user = request.form["username"]
        passw = sha256(request.form["password"].encode('utf-8')).hexdigest()
        if User.objects(username = user, password = passw):
            Userobj = User.objects(username = user, password = passw).first()
            print(Userobj.to_json())
            session["user"] = Userobj.to_json()
            return make_response("Login Success", 200)
        else:
            return make_response("Wrong username or password", 400)


@app.route("/logout", methods = ['POST'])
def logout(): 
    if "user" in session:
        session.pop("user", None)
        return make_response("Success", 200)
    else:
        return make_response("User not logged in", 400)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug = True)