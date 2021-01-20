from wtforms import StringField, TextAreaField, SelectField, PasswordField, BooleanField, HiddenField, RadioField, DateField, FloatField, FileField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField, EmailField
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import email_validator

class CompanyRegister(FlaskForm):
    username = StringField("User Name", validators=[DataRequired(message="Please enter a user name")])
    name = StringField("Company Name", validators=[DataRequired(message="Please enter a company name")])
    taxnumber = StringField("Tax Number", validators=[DataRequired("Please enter a tax number"), Length(10,10,"Your tax number must contain 10 characters")])
    email = EmailField("E-mail", validators=[Email(message= "Please enter a valid e-mail")])
    password = PasswordField("Password", validators=[ DataRequired(message="Please enter a password"), EqualTo(fieldname="confirm", message="Your passwords are not match")])
    confirm = PasswordField("Enter your password again", validators=[DataRequired()])
    servicetype = RadioField("Service Type", validate_choice=False)
    city = SelectField(u'City', validate_choice=False)
    check = BooleanField("I agree with terms and conditions", validators=[DataRequired("You must accept terms and conditions")])
    file = FileField("Logo of your company")

class CompanyProfile(FlaskForm):
    username = StringField("User Name", validators=[DataRequired(message="Please enter a user name")])
    name = StringField("Company Name", validators=[DataRequired(message="Please enter a company name")])
    taxnumber = StringField("Tax Number", validators=[DataRequired("Please enter a tax number"), Length(10,10,"Your tax number must contain 10 characters")])
    email = EmailField("E-mail", validators=[Email(message= "Please enter a valid e-mail")])
    servicetype = RadioField("Service Type", validate_choice=False)
    city = SelectField(u'City', validate_choice=False)
    file = FileField("Logo of your company")

class ConsumerRegister(FlaskForm):
    username = StringField(label=("User Name"), validators=[DataRequired(message="Please enter a user name")])
    name = StringField(label=("Name"), validators=[DataRequired(message="Please enter a  name")])
    surname = StringField(label=("Surname"), validators=[DataRequired(message="Please enter a surname")])
    identitynum = StringField(label=("Identity Number"), validators=[DataRequired("Please enter an ID"), Length(11,11,"Your ID must consist of 11 digits")])
    address = TextAreaField(label=("Address"), validators=[DataRequired("Please enter your address"), Length(1,256,"Address should be smaller than 256 characters")])
    email = EmailField("E-mail", validators=[Email(message= "Please enter a valid e-mail")])
    password = PasswordField("Password", validators=[ DataRequired(message="Please enter a password"), EqualTo(fieldname="confirm", message="Your passwords are not match")])
    confirm = PasswordField("Enter your password again")
    city = SelectField(u'City', validate_choice=False)
    check = BooleanField("I agree with terms and conditions", validators=[DataRequired("You must accept terms and conditions")])

class ConsumerProfile(FlaskForm):
    username = StringField(label=("User Name"), validators=[DataRequired(message="Please enter a user name")])
    name = StringField(label=("Name"), validators=[DataRequired(message="Please enter a  name")])
    surname = StringField(label=("Surname"), validators=[DataRequired(message="Please enter a surname")])
    identitynum = StringField(label=("Identity Number"), validators=[DataRequired("Please enter an ID"), Length(11,11,"Your ID must consist of 11 digits")])
    address = TextAreaField(label=("Address"), validators=[DataRequired("Please enter your address"), Length(1,256,"Address should be smaller than 256 characters")])
    email = EmailField("E-mail", validators=[Email(message= "Please enter a valid e-mail")])
    city = SelectField(u'City', validate_choice=False)

class Login(FlaskForm):
    username = StringField("User Name", validators=[DataRequired("Please enter a username")])
    password = PasswordField("Password", validators=[DataRequired("Please enter a password")])

class Invoice(FlaskForm):
    name = StringField(label=("Name of the consumer"))
    surname = StringField(label=("Surname of the consumer"))
    billnum = StringField(label=("Invoice Number"))
    billnumhidden = HiddenField()
    invoiceDate = DateField(label="Invoice Date")
    deadline = DateField(label="Deadline for payment")
    charge = FloatField(label=("Charge"))
    taxrate = FloatField(label=("Tax Rate"), validators=[DataRequired("Please enter a tax rate. Try again!"), NumberRange(0,100,"Tax rate should be between 0-100. Try again!")])

class InvoiceEdit(FlaskForm):
    invoiceDate = DateField(label=("Invoice Date"))
    deadline = DateField(label=("Deadline"))
    charge = FloatField(label=("Charge"), validators=[DataRequired("Please enter a charge")])
    taxrate = FloatField(label=("Tax Rate"), validators=[DataRequired("Please enter a tax rate. Try again!"), NumberRange(0,100,"Tax rate should be between 0-100. Try again!")])

class BankAccount(FlaskForm):
    name = StringField("Bank Account Name", validators=[DataRequired(message="Please give a name to your bank account")])
    iban = StringField("IBAN", validators=[DataRequired(message="Please enter your IBAN number"), Length(26, 26, "Your IBAN must contains 26 characters")])
    balance = FloatField("Balance", validators=[DataRequired(message="Please enter balance of your bank account")])

class DrawMoney(FlaskForm):
    money = FloatField("Money", validators=[DataRequired(message="Please enter a number")])

class Outage(FlaskForm):
    startDate = DateField(label="Start Date")
    endDate = DateField(label="End Date")