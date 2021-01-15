from wtforms import Form, StringField, TextAreaField, SelectField, PasswordField, validators
from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as hasher
import psycopg2 as dbapi2
import os
import sys

class CompanyRegister(Form):
    username = StringField("User Name", validators=[validators.DataRequired(message="Please enter a user name")])
    name = StringField("Company Name", validators=[validators.DataRequired(message="Please enter a company name")])
    #email = StringField("E-mail", validators=[validators.Email(message= "Please enter a valid e-mail")])
    password = PasswordField("Password", validators=[
            validators.DataRequired(message="Please enter a password"),
            validators.EqualTo(fieldname="confirm", message="Your passwords are not match")])
    confirm = PasswordField("Enter your password again")
    servicetype = SelectField(u'Service Type', validate_choice=False)
    city = SelectField(u'City', validate_choice=False)


class ConsumerRegister(Form):
    username = StringField(label=("User Name"), validators=[validators.DataRequired(message="Please enter a user name")])
    name = StringField(label=("Name"), validators=[validators.DataRequired(message="Please enter a  name")])
    surname = StringField(label=("Surname"), validators=[validators.DataRequired(message="Please enter a surname")])
    email = StringField("E-mail")
    password = PasswordField("Password", validators=[
            validators.DataRequired(message="Please enter a password"),
            validators.EqualTo(fieldname="confirm", message="Your passwords are not match")])
    confirm = PasswordField("Enter your password again")
    city = SelectField(u'City', validate_choice=False)


class Login(Form):
    username = StringField(label=("User Name"), validators=[validators.DataRequired(message="Please enter a user name")])
    password = PasswordField("Password", validators=[validators.DataRequired(message="Please enter a password")])