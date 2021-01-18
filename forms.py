from wtforms import Form, StringField, TextAreaField, SelectField, PasswordField, BooleanField, HiddenField, RadioField, DateField, FloatField, FileField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo
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
    password = PasswordField("Password", validators=[
            DataRequired(message="Please enter a password"),
            EqualTo(fieldname="confirm", message="Your passwords are not match")])
    confirm = PasswordField("Enter your password again", validators=[DataRequired()])
    servicetype = RadioField("Service Type", validate_choice=False)
    city = SelectField(u'City', validate_choice=False)
    check = BooleanField("I agree with terms and conditions", validators=[DataRequired("You must accept terms and conditions")])
    file = FileField("Logo of your company")

class ConsumerRegister(Form):
    username = StringField(label=("User Name"), validators=[DataRequired(message="Please enter a user name")])
    name = StringField(label=("Name"), validators=[DataRequired(message="Please enter a  name")])
    surname = StringField(label=("Surname"), validators=[DataRequired(message="Please enter a surname")])
    identitynum = StringField(label=("Identity Number"), validators=[DataRequired("Please enter an ID"), Length(11,11,"Your ID must consist of 11 digits")])
    address = TextAreaField(label=("Address"), validators=[DataRequired("Please enter your address"), Length(1,256,"Address should be smaller than 256 characters")])
    email = EmailField("E-mail", validators=[Email(message= "Please enter a valid e-mail")])
    password = PasswordField("Password", validators=[
            validators.DataRequired(message="Please enter a password"),
            validators.EqualTo(fieldname="confirm", message="Your passwords are not match")])
    confirm = PasswordField("Enter your password again")
    city = SelectField(u'City', validate_choice=False)
    check = BooleanField("I agree with terms and conditions", validators=[DataRequired("You must accept terms and conditions")])


class Login(Form):
    username = StringField(label=("User Name"), validators=[validators.DataRequired(message="Please enter a user name")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please enter a password")])

class Invoice(Form):
    name = StringField(label=("Name of the consumer"))
    surname = StringField(label=("Surname of the consumer"))
    billnum = StringField(label=("Invoice Number"))
    billnumhidden = HiddenField()
    invoiceDate = DateField(label="Invoice Date")
    deadline = DateField(label="Deadline for payment")
    charge = FloatField(label=("Charge"))

class InvoiceEdit(Form):
    invoiceDate = DateField(label=("Invoice Date"))
    deadline = DateField(label=("Deadline"))
    charge = FloatField(label=("Charge"))
    lateFee = FloatField(label=("Late Fee"))

class BankAccount(Form):
    name = StringField("Bank Account Name", validators=[validators.DataRequired(message="Please give a name to your bank account")])
    iban = StringField("IBAN", validators=[validators.DataRequired(message="Please enter your IBAN number"), validators.Length(26, 26, "Your IBAN must contaion 26 characters")])
    balance = FloatField("Balance", validators=[validators.DataRequired(message="Please enter balance of your bank account")])

class Outage(Form):
    startDate = DateField(label="Start Date")
    endDate = DateField(label="End Date")