# -*- coding: utf-8 -*-
import os
from checks import *
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash


# initialization
app = Flask(__name__)
#create key for the token encryption
app.config['SECRET_KEY'] = 'ROI hunter test'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)
# Instance of the authentification manager
auth = HTTPBasicAuth()

class Account(db.Model):
	#Create table and rows
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    active = db.Column(db.Boolean)
    #Encrypt password
    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

#Verify if account: exist, is active, correct credentials
@auth.verify_password
def verify_password(username, password):
    account = Account.query.filter_by(username=username).first()
    if not account or not account.verify_password(password) or not account.active:
        return False
    g.account = account
    return True

#Create accounts
@app.route('/createAccount', methods = ['POST'])
def new_account():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if Account.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    account = Account(username = username, active= True)
    account.hash_password(password)
    db.session.add(account)
    db.session.commit()
    return jsonify({ 'Your account have been created': account.username })

#Deactivate account (not delete them). Till is deleted no new account with this name can be created
@app.route('/deactivateAccount', methods = ['POST'])
def delete_account():
	username = request.json.get('username')
	password = request.json.get('password')
	account = Account.query.filter_by(username=username).first()
	if username is None or password is None:
		abort(400) # missing arguments
	if account is None or not account.active or not account.verify_password(password):
		abort(400) # none existing user or wrong pass
	account = Account.query.filter_by(username=username).first()
	account.active = False
	db.session.commit()
	return jsonify({ 'Your account have deleted': account.username })


@app.route("/")
def hello_world():
    return "Hello world"


@app.route("/hello/<name>")
def say_hello(name):
    return f"Hello <b>{name}</b>"


@app.route("/metrics/cpu")
@auth.login_required
def metrics_cpu():
    return cpucheck()


@app.route("/metrics/ram")
@auth.login_required
def metrics_ram():
    return memorycheck()


@app.route("/metrics/disk")
@auth.login_required
def metrics_disk():
    return diskcheck()


@app.route("/metrics/network")
@auth.login_required
def metrics_network():
    return netcheck()


@app.route("/metrics/services")
@auth.login_required
def metrics_services():
	return servicheck()


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
    	db.create_all()
    app.run(debug=True, host='0.0.0.0')