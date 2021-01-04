from flask import Flask, render_template
from datetime import datetime


app = Flask(__name__)

@app.route("/")
def homePage():
    today = datetime.today()
    dayName = today.strftime("%A")
    return render_template("index.html")

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
    app.run(host="0.0.0.0", port="8080", debug=True)
