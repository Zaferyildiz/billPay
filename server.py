from wtforms import Form, StringField, TextAreaField, SelectField, PasswordField, validators
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as hasher
import psycopg2 as dbapi2
import os
import sys
from dboperations import *
from forms import *

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route("/", methods = ["GET", "POST"])
def index(): 
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login(): 
    form = Login(request.form)
    if request.method == "POST":
        username = form.username.data
        passwordInput = form.password.data
        res = isLogin(username, passwordInput)
        if res == "nouser":
            flash("There is no user with this username", "danger")
            error = "There is no user with this username"
            return redirect(url_for("login"))
        elif res == "wrongpassword":
            flash("Your password is wrong! Please try again!", "danger")
            return redirect(url_for("login"))
        else:
            return redirect(url_for("index"))
    else: 
        return render_template("login.html", form=form)


@app.route("/company/register", methods = ["GET", "POST"])
def companyRegister():
    form = CompanyRegister(request.form)
    if request.method == "POST" and form.validate(): 
        username = form.username.data
        name = form.name.data
        email = form.email.data
        password = form.password.data
        serviceTypeId = form.servicetype.data
        cityId = form.city.data
        saveCompany(username, name, email, password, serviceTypeId, cityId)  
        flash("You have succesfully registered!", "success")
        return redirect("/company/register")
    else:
        city = getAllCities()
        servicetype = getAllServiceTypes()
        form.servicetype.choices = [(s['id'], s['name']) for s in servicetype]
        form.city.choices = [(c['id'], c['name']) for c in city]    
        return render_template("companyRegister.html", form=form)
        

@app.route("/consumer/register", methods = ["GET", "POST"])
def consumerRegister():
    form = ConsumerRegister(request.form)
    if request.method == "POST":
        username = form.username.data
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        password = form.password.data
        cityId = form.city.data
        saveConsumer(username, name, surname, email, password, cityId)    
        return redirect("/")
        
    else:
        city = getAllCities()
        form.city.choices = [(c['id'], c['name']) for c in city]    
        return render_template("consumerRegister.html", form=form)

@app.route("/myBills")
def myBillPage():
    return render_template("myBill.html")

@app.route("/donate")
def donationBills():
    return render_template("donate.html")

@app.route("/bankAccount")
def bankAccount():
    return render_template("bankAccount.html")

@app.route("/outage")
def outage():
    return render_template("outages.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8080", debug=True)
