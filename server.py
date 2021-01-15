from wtforms import Form, StringField, TextAreaField, SelectField, PasswordField, validators
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as hasher
from functools import wraps
import psycopg2 as dbapi2
import os
import sys
from random import *
from db import *
from forms import *
from decorator import *

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
        if res[0] == "company":
            company = res[1]
            if hasher.verify(passwordInput, company['password']):
                flash("Your login is successfull", "success")
                session['loggedin'] = True
                session['id'] = company['id']
                session['username'] = company['username']
                session['role'] = "company"
                return redirect(url_for("index"))
            else:
                flash("Your password is wrong! Please try again!", "danger")
                return redirect(url_for("login"))
        elif res[0] == "consumer":
            consumer = res[1]
            if hasher.verify(passwordInput, consumer['password']):
                flash("Your login is successfull consumer x", "success")
                session['loggedin'] = True
                session['id'] = consumer['id']
                session['username'] = consumer['username']
                session['role'] = "consumer"
                return redirect(url_for("index"))
            else:
                flash("Your password is wrong! Please try again!", "danger")
                return redirect(url_for("login"))
        else:
            flash("There is no user with this username", "danger")
            return redirect(url_for("login"))
    else: 
        return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/company/register", methods = ["GET", "POST"])
def companyRegister():
    form = CompanyRegister(request.form)
    if request.method == "POST" and form.validate(): 
        username = form.username.data
        name = form.name.data
        email = form.email.data
        password = hasher.hash(form.password.data)
        serviceTypeId = form.servicetype.data
        cityId = form.city.data
        saveCompany(username, name, email, password, serviceTypeId, cityId)  
        flash("You have succesfully registered!", "success")
        return redirect(url_for("companyRegister"))
    else:
        city = getAllCities()
        servicetype = getAllServiceTypes()
        form.servicetype.choices = [(s['id'], s['name']) for s in servicetype]
        form.city.choices = [(c['id'], c['name']) for c in city]    
        return render_template("/company/register.html", form=form)
        
@app.route("/company/profile", methods = ["GET", "POST"])
@isCompany
def companyProfile():
    form = CompanyRegister(request.form)
    if request.method == "POST":
        companyId = session['id']
        username = form.username.data
        name = form.name.data
        email = form.email.data
        serviceTypeId = form.servicetype.data
        cityId = form.city.data
        updateCompany(companyId, username, name, email, serviceTypeId, cityId)
        return redirect(url_for("companyProfile"))
    else:
        company = getCompany(session['id'])
        form.username.default = company['username']
        form.name.default = company['name']
        form.email.default = company['email']
        city = getAllCities()
        form.city.choices = [(c['id'], c['name']) for c in city] 
        form.city.default = company['cityid']
        servicetypes = getAllServiceTypes()
        form.servicetype.choices = [(s['id'], s['name']) for s in servicetypes]
        form.servicetype.default = company['servicetypeid']
        form.process()
        return render_template("company/profile.html", form=form)

@app.route("/consumer/register", methods = ["GET", "POST"])
def consumerRegister():
    form = ConsumerRegister(request.form)
    if request.method == "POST":
        username = form.username.data
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        password = hasher.hash(form.password.data)
        cityId = form.city.data
        saveConsumer(username, name, surname, email, password, cityId)    
        return redirect("/")     
    else:
        city = getAllCities()
        form.city.choices = [(c['id'], c['name']) for c in city]    
        return render_template("consumer/register.html", form=form)

@app.route("/consumer/profile", methods = ["GET", "POST"])
@isConsumer
def consumerProfile():
    form = ConsumerRegister(request.form)
    if request.method == "POST":
        consumerId = session['id']
        username = form.username.data
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        cityId = form.city.data
        updateConsumer(consumerId, username, name, surname, email, cityId)
        return redirect(url_for("consumerProfile"))
    else:
        consumer = getConsumer(session['id'])
        form.username.default = consumer['username']
        form.name.default = consumer['name']
        form.surname.default = consumer['surname']
        form.email.default = consumer['email']
        city = getAllCities()
        form.city.choices = [(c['id'], c['name']) for c in city] 
        form.city.default = consumer['cityid']
        form.process()
        return render_template("consumer/profile.html", form=form)

@app.route("/consumer/profile/delete", methods = ["POST"])
@isConsumer
def consumerDelete():
    form = ConsumerRegister(request.form)
    if request.method == "POST":
        consumerId = session['id']
        deleteConsumer(consumerId)
        session.clear()
        return redirect(url_for("index"))

@app.route("/company/profile/delete", methods = ["POST"])
@isCompany
def companyDelete():
    companyId = session['id']
    deleteCompany(companyId)
    session.clear()
    return redirect(url_for("index"))

@app.route("/makeoutinvoice")
def makeOutInvoice():
    consumers = getAllConsumer()
    return render_template("company/makeinvoice.html", consumers=consumers)

@app.route("/createInvoice/<int:consumerId>", methods=["GET", "POST"])
def createInvoice(consumerId):
    consumer = getConsumer(consumerId)
    charge = "{:.2f}".format(random() * 100 + 40)

    if request.method == "POST":
        date = datetime.today()
        #sevenday = datetime.timedelta(days=7)
        deadline = date
        company = getCompany(session['username'])
        makeInvoice(date, deadline, company['id'], company['servicetypeid'], consumerId, charge) 
        flash("Invoice is created","Success")
        return redirect(url_for("makeOutInvoice"))   
    else:
        return render_template("company/createInvoice.html", consumer=consumer, charge=charge)

@app.route("/myBills/", defaults={'billId': None}, methods=["GET","POST"])
@app.route("/myBills/<string:billId>", methods=["GET","POST"])
@isConsumer
def myBills(billId):
    if request.method == "POST":
        deleteBill(billId)
        return redirect(url_for("myBills"))
    else:
        bills = getMyBills(session['id'])
        return render_template("consumer/myBill.html", bills=bills)

@app.route("/myBills/donateBill/<string:billId>", methods=["POST"])
@isConsumer
def shareBill(billId):
    billShare(billId)
    return redirect(url_for("myBills"))

@app.route("/donate")
@isConsumer
def donationBills():
    data = getDonatedBills()
    return render_template("consumer/donate.html", donatedBills=data)

@app.route("/bankAccount")
def bankAccount():
    return render_template("bankAccount.html")

@app.route("/outages")
def outages():
    return render_template("consumer/outages.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="8080", debug=True)