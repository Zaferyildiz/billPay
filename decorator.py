from flask import session, flash, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' in session:
            return f(*args, **kwargs)
        else:
            flash("You should log in to view this page", "danger")
            return redirect(url_for("login"))
    return decorated_function

def isCompany(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' in session and session['role'] == 'company':
            return f(*args, **kwargs)
        else:
            flash("You should log in as company to view this page", "danger")
            return redirect(url_for("login"))
    return decorated_function

def isConsumer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' in session and session['role'] == 'consumer':
            return f(*args, **kwargs)
        else:
            flash("You should log in as consumer to view this page", "danger")
            return redirect(url_for("login"))
    return decorated_function