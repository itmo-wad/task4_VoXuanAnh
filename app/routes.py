from flask import render_template, send_from_directory, request, redirect, Flask, session, make_response
from app import app
from pymongo import MongoClient
import time

client = MongoClient('localhost', 27017)
db = client.authen_DB



@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', message="Please enter your username and password")
    if request.method == 'POST':
        input_uname = str(request.form.get("uname"))
        input_pwd = str(request.form.get("pwd"))
        number_of_documents = db.authen.count_documents({})
        print("Total number of documents: " + str(number_of_documents))
        t = time.time()
        check_existed_user = db.authen.find_one({"username": input_uname})
        print("Checking existed user with index for " + str(number_of_documents) + f" users time = {time.time() - t}")
        if (check_existed_user != None):
            if (check_existed_user["password"] == input_pwd):
                resp = make_response(redirect('cabinet'))
                resp.set_cookie('userID', value=str(input_uname))
                print(resp)
                return resp
        return render_template('login.html', message="Not correct username or password!")

   

@app.route('/cabinet')
def cabinet():
    state = request.cookies.get("loggedIn")
    if (state != ''):
        return render_template('index.html')
    return render_template('login.html', message="You have to log in first")


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', message='')
    if request.method == 'POST':
        input_uname = str(request.form.get("uname"))
        input_pwd = str(request.form.get("pwd"))
        check_existed_user = db.authen.find_one({"username": input_uname})
        if (check_existed_user == None):
            db.authen.insert({
                "username": input_uname,
                "password": input_pwd
            })
            return render_template('login.html', message='Register successful!')
        else:
            return render_template('register.html', message='User already exists!')
        

@app.route('/images/<path:filename>')
def custom_static(filename):
    return send_from_directory('images', filename)

@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('userID', value='')
    return resp

@app.route('/changepwd', methods=['GET', 'POST'])
def changepwd():
    uname = str(request.cookies.get('userID'))
    if request.method == 'GET':
        return render_template('changepwd.html', username = uname)
    if request.method == 'POST':
        input_pwd1 = str(request.form.get("pwd1"))
        input_pwd2 = str(request.form.get("pwd2"))
        if (input_pwd1 != input_pwd2):
            return render_template('changepwd.html', username = uname, message='Password did not match!')
        else:
            db.authen.update_one({"username": uname},{"$set": {"password": input_pwd1}})
            return render_template('login.html', message="You have to log in with the new password")

    
