from flask import Flask, render_template, request, redirect
from datetime import datetime
#from passlib.hash import pbkdf2_sha256 as hasher
import psycopg2 as dbapi2
import os
import sys

app = Flask(__name__)
url = os.getenv("DATABASE_URL")

@app.route("/", methods = ["GET", "POST"])
def homePage(): 
    return render_template("index.html")
    

@app.route("/company/register", methods = ["GET", "POST"])
def companyRegister():
    if request.method == "GET": 
        with dbapi2.connect(url) as connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM public.servicetype")
            servicetype = cur.fetchall()
            cur.execute("SELECT * FROM public.city")
            city = cur.fetchall()
            return render_template("companyRegister.html", servicetype=servicetype, city=city)
    else:
        with dbapi2.connect(url) as connection:
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            serviceTypeId = request.form["servicetype"]
            cityId = request.form["city"]
            cursor = connection.cursor()
            query = """INSERT INTO COMPANY (NAME, EMAIL, PASSWORD, SERVICETYPEID, CITYID) VALUES(%s,%s,%s,%s,%s); """
            cursor.execute(query, (name,email,password, serviceTypeId, cityId) )
            connection.commit()
            cursor.close()
        return redirect("/")

@app.route("/consumer/register", methods = ["GET", "POST"])
def consumerRegister():
    if request.method == "GET": 
        with dbapi2.connect(url) as connection:
            cur = connection.cursor()
            cur.execute("SELECT * FROM public.city")
            city = cur.fetchall()
        return render_template("consumerRegister.html", city=city)
    else:
        with dbapi2.connect(url) as connection:
            name = request.form["name"]
            surname = request.form["surname"]
            email = request.form["email"]
            password = request.form["password"]
            cityId = request.form["city"]
            cursor = connection.cursor()
            query = """INSERT INTO CONSUMER (NAME, SURNAME, EMAIL, PASSWORD, CITYID) VALUES(%s,%s,%s,%s,%s); """
            cursor.execute(query, (name, surname, email, password, cityId) )
            connection.commit()
            cursor.close()
        return redirect("/")


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
