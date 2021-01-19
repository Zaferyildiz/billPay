from flask import Flask, render_template, request, redirect, session, url_for
from wtforms import Form, StringField, TextAreaField, SelectField, PasswordField, validators
from flask_wtf import FlaskForm
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256 as hasher
from functools import wraps
import psycopg2 as dbapi2
import os
import sys
import string
import random
from db import *
from forms import *
from decorator import *
import base64

app = Flask(__name__)
app.secret_key = "super secret key"

@app.route("/")
def index():
    nofcompany = getNumberofCompany()
    nofconsumer = getNumberofConsumer()
    nofcity = getNumberofCity()
    return render_template("index.html", numberofConsumer=nofconsumer, numberofCompany=nofcompany, numberofCity=nofcity)

@app.route("/login", methods = ["GET", "POST"])
def login(): 
    form = Login(request.form)
    if request.method == "POST" and form.validate():
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
                session['name'] = company['name']
                session['role'] = "company"
                return redirect(url_for("index"))
            else:
                flash("Your password is wrong! Please try again!", "danger")
                return redirect(url_for("login"))
        elif res[0] == "consumer":
            consumer = res[1]
            if hasher.verify(passwordInput, consumer['password']):
                flash("Your login is successfull", "success")
                session['loggedin'] = True
                session['id'] = consumer['id']
                session['name'] = consumer['name']
                session['surname'] = consumer['surname']
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
    if request.method == "POST": 
        username = form.username.data
        name = form.name.data
        taxnumber = form.taxnumber.data
        email = form.email.data
        password = hasher.hash(form.password.data)
        serviceTypeId = form.servicetype.data
        cityId = form.city.data
        logo = request.files['file']
        encoded = base64.b64encode(logo.read())
        saveCompany(username, name, taxnumber, email, password, serviceTypeId, cityId, encoded)  
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
        taxnumber = form.taxnumber.data
        email = form.email.data
        serviceTypeId = form.servicetype.data
        cityId = form.city.data
        updateCompany(companyId, username, name, taxnumber, email, serviceTypeId, cityId)
        return redirect(url_for("companyProfile"))
    else:
        company = getCompany(session['id'])
        form.username.default = company['username']
        form.name.default = company['name']
        form.taxnumber.default = company['taxnumber']
        form.email.default = company['email']
        city = getAllCities()
        form.city.choices = [(c['id'], c['name']) for c in city] 
        form.city.default = company['cityid']
        servicetypes = getAllServiceTypes()
        form.servicetype.choices = [(s['id'], s['name']) for s in servicetypes]
        form.servicetype.default = company['servicetypeid']
        form.process()
        logo = getlogo(session['id'])
        return render_template("company/profile.html", form=form, logo=logo)

@app.route("/consumer/register", methods = ["GET", "POST"])
def consumerRegister():
    form = ConsumerRegister(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        name = form.name.data
        surname = form.surname.data
        identitynum = form.identitynum.data
        email = form.email.data
        password = hasher.hash(form.password.data)
        cityId = form.city.data
        address = form.address.data
        saveConsumer(username, name, surname, identitynum, email, password, cityId, address)    
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
        print("girdi2")
        consumerId = session['id']
        username = form.username.data
        name = form.name.data
        surname = form.surname.data
        idnumber = form.identitynum.data
        email = form.email.data
        cityId = form.city.data
        address = form.address.data
        updateConsumer(consumerId, username, name, surname, idnumber, email, cityId, address)
        return redirect(url_for("consumerProfile"))
    else:
        consumer = getConsumer(session['id'])
        form.username.default = consumer['username']
        form.name.default = consumer['name']
        form.surname.default = consumer['surname']
        form.identitynum.default = consumer['identitynum']
        form.email.default = consumer['email']
        city = getAllCities()
        form.city.choices = [(c['id'], c['name']) for c in city] 
        form.city.default = consumer['cityid']
        form.address.default = consumer['address']
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

@app.route("/consumers")
@isCompany
def viewConsumers():
    consumers = getAllConsumer()
    return render_template("company/viewConsumers.html", consumers=consumers)

@app.route("/createInvoice/<int:consumerId>", methods=["GET", "POST"])
@isCompany
def createInvoice(consumerId):
    consumer = getConsumer(consumerId)
    form = Invoice(request.form)
    charge = "{:.2f}".format(random.random() * 100 + 40)
    
    if request.method == "POST":
        billnum = form.billnumhidden.data
        invoicedate = datetime.today()
        deadline = form.deadline.data
        charge = form.charge.data 
        companyId = session['id']
        makeInvoice(billnum, invoicedate, deadline, charge, companyId, consumerId) 
        flash("Invoice is created","Success")
        return redirect(url_for("viewConsumers"))   
    else:
        dateoftoday = datetime.today()
        deadline = dateoftoday + timedelta(days=7)
        billnum = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(16))
        form.name.default = consumer['name']
        form.surname.default = consumer['surname']
        form.billnum.default = billnum
        form.billnumhidden.default = billnum
        form.charge.default = charge
        form.invoiceDate.default = dateoftoday
        form.deadline.default = deadline
        form.process()
        return render_template("company/createInvoice.html", form=form, consumer=consumer, charge=charge)

@app.route("/invoicesOfConsumer/<int:consumerId>", methods=["GET", "POST"])
@isCompany
def viewInvoicesofConsumer(consumerId):
    invoices = getInvoiceofConsumer(consumerId)
    consumer = getConsumer(consumerId)
    if request.method == "POST":
        editInvoice(date, deadline, company['id'], company['servicetypeid'], consumerId, charge) 
        flash("Invoice is created","Success")
        return redirect(url_for("viewInvoice"))   
    else:
        return render_template("company/invoicesofConsumer.html", invoices=invoices, consumer=consumer)

@app.route("/invoice/delete/<int:billId>/<int:consumerId>", methods=["POST"])
@isCompany
def deleteInvoice(billId, consumerId):
    if request.method == "POST":
        deleteBill(billId)
        flash("Invoice is deleted","Success")
        return redirect(url_for("viewInvoicesofConsumer", consumerId=consumerId))   
    else:
        return redirect(url_for("viewInvoicesofConsumer", consumerId=consumerId))


@app.route("/invoice/<int:billId>", methods=["GET", "POST"])
@isCompany
def viewInvoice(billId):
    invoice = getInvoice(billId)
    form = InvoiceEdit(request.form)
    if request.method == "POST" :
        invoiceDate = form.invoiceDate.data
        deadline = form.deadline.data
        charge = form.charge.data
        editInvoice(billId, invoiceDate, deadline, charge) 
        return redirect(url_for("viewInvoice", billId=billId))   
    else:
        form.invoiceDate.default = invoice['invoicedate']
        form.charge.default = invoice['charge']
        form.deadline.default = invoice['deadline']
        form.process()
        return render_template("company/viewInvoice.html", invoice=invoice, form=form)


@app.route("/myBills/", defaults={'billId': None}, methods=["GET","POST"])
@app.route("/myBills/<string:billId>", methods=["GET","POST"])
@isConsumer
def myBills(billId):
    if request.method == "POST":
        bill = getInvoice(billId)
        mybankaccount = getBankAccount(session['id'], "consumer")
        if mybankaccount['balance'] >= bill['charge']:
            deleteBill(billId)
        else:
            flash("Your balance is not enough for this operation", "danger")
        return redirect(url_for("myBills"))
    else:
        bills = getMyBills(session['id'])
        return render_template("consumer/myBill.html", bills=bills)

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    native = date.replace(tzinfo=None)
    format='%d/%m/%Y'
    return native.strftime(format)

@app.route("/myBills/donateBill/<string:billId>", methods=["POST"])
@isConsumer
def shareBill(billId):
    billShare(billId)
    return redirect(url_for("myBills"))

@app.route("/createOutage", methods=["GET", "POST"])
@isCompany
def createOutage():
    form = Outage(request.form)
    if request.method == "POST" and form.validate():
        startDate = form.startDate.data
        endDate = form.endDate.data
        companyId = session['id']
        addOutage(startDate, endDate, companyId)
        flash("Outage is created", "success")
        return redirect(url_for("createOutage"))
    else:
        return render_template("/company/createOutage.html", form=form)

@app.route("/donate")
@isConsumer
def donationBills():
    data = getDonatedBills()
    return render_template("consumer/donate.html", donatedBills=data)

@app.route("/bankAccount", methods=["GET", "POST"])
def bankAccount():
    form = BankAccount(request.form)
    moneyform = DrawMoney(request.form)
    if request.method == "POST":
        name = form.name.data
        iban = form.iban.data
        balance = form.balance.data
        bankAccountId = createBankAccount(name, iban, balance)
        if session['role'] == "company":
            assignBankAccounttoCompany(bankAccountId, session['id'])
        else:
            assignBankAccounttoConsumer(bankAccountId, session['id'])
        return redirect(url_for("bankAccount"))
    else:
        account = getBankAccount(session['id'], session['role'])
        if not account:
            return render_template("bankAccount.html", form=form, moneyform=moneyform, bankaccount=account)
        else:
            form.name.default = account['name']
            form.iban.default = account['iban']
            form.balance.default = account['balance']
            form.process()
            return render_template("bankAccount.html", form=form,  moneyform=moneyform, bankaccount=account)

@app.route("/drawmoney/<int:bankAccountId>", methods=["POST"])
def drawMoney(bankAccountId):
    form = DrawMoney(request.form)
    money = form.money.data
    bankAccountDrawMoney(bankAccountId, money)
    return redirect(url_for("bankAccount"))

@app.route("/outages")
@isConsumer
def outages():
    consumer = getConsumer(session['id'])
    cityId = consumer['cityid']
    outages = getOutages(cityId)
    return render_template("consumer/outages.html", outages=outages)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port="5000", debug=True)