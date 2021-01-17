from wtforms import Form, StringField, TextAreaField, SelectField, PasswordField, BooleanField, RadioField, DateField, FloatField, FileField, validators
from wtforms.fields.html5 import DateField, EmailField
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import email_validator


class CompanyRegister(Form):
    username = StringField("User Name", validators=[validators.DataRequired(message="Please enter a user name")])
    name = StringField("Company Name", validators=[validators.DataRequired(message="Please enter a company name")])
    email = EmailField("E-mail", validators=[validators.Email(message= "Please enter a valid e-mail")])
    password = PasswordField("Password", validators=[
            validators.DataRequired(message="Please enter a password"),
            validators.EqualTo(fieldname="confirm", message="Your passwords are not match")])
    confirm = PasswordField("Enter your password again")
    servicetype = RadioField("Service Type", validators=[validators.DataRequired()])
    city = SelectField(u'City', validate_choice=False)
    check = BooleanField("I agree with terms and conditions", validators=[validators.DataRequired("You must accept terms and conditions")])


class ConsumerRegister(Form):
    username = StringField(label=("User Name"), validators=[validators.DataRequired(message="Please enter a user name")])
    name = StringField(label=("Name"), validators=[validators.DataRequired(message="Please enter a  name")])
    surname = StringField(label=("Surname"), validators=[validators.DataRequired(message="Please enter a surname")])
    email = EmailField("E-mail", validators=[validators.Email(message= "Please enter a valid e-mail")])
    password = PasswordField("Password", validators=[
            validators.DataRequired(message="Please enter a password"),
            validators.EqualTo(fieldname="confirm", message="Your passwords are not match")])
    confirm = PasswordField("Enter your password again")
    city = SelectField(u'City', validate_choice=False)
    check = BooleanField("I agree with terms and conditions", validators=[validators.DataRequired("You must accept terms and conditions")])


class Login(Form):
    username = StringField(label=("User Name"), validators=[validators.DataRequired(message="Please enter a user name")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please enter a password")])

class InvoiceEdit(Form):
    invoiceDate = DateField(label=("Invoice Date"))
    deadline = DateField(label=("Deadline"))
    charge = FloatField(label=("Charge"))
    lateFee = FloatField(label=("Late Fee"))

class BankAccount(Form):
    name = StringField("Bank Account Name", validators=[validators.DataRequired(message="Please give a name to your bank account")])
    iban = StringField("IBAN", validators=[validators.DataRequired(message="Please enter your IBAN number"), validators.Length(26, 26, "Your IBAN should contains of 26 characters")])
    balance = FloatField("Balance", validators=[validators.DataRequired(message="Please enter balance of your bank account")])

class Outage(Form):
    startDate = DateField(label="Start Date")
    endDate = DateField(label="End Date")