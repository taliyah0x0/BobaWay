from flask import Flask, request, render_template, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from deep_translator import GoogleTranslator
import requests
import os
import random
from datetime import datetime
from bs4 import BeautifulSoup
from pydub import AudioSegment
import csv
import numpy as np
import pinyin
import pyppeteer
import webbrowser
import re

# Local imports
from clean_csvs import clean_csv_1, clean_csv_2, clean_3_4_combined
from constants import num, consonants, vowels, match_lett
from bobaway_utils import load_exceptions, add_tones
from sinodb import SinoDB
from secrets import SECRET_KEY
from forms import LoginForm, SignupForm
from user import User
from sinotype_utils import checkHanzi, checkRoman, checkEntryExistence


cleaned_1 = clean_csv_1()
cleaned_2 = clean_csv_2()
cleaned_3_4 = clean_3_4_combined()

# Create 2 lists for search terms vs. romanization
src_1_search = []
src_1_code = []
src_1_tai = []
for row in cleaned_1:
  src_1_search.append(row[0])
  src_1_code.append(row[1])
  src_1_tai.append(row[2])


app = Flask(__name__)
app.secret_key = SECRET_KEY

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'adminloginpage'


@app.route("/", methods=["GET", "POST"])
def bobaway():
  return render_template("index.html")

@app.route("/sino-type", methods=["GET"])
def sino_type():
  return render_template("sino-type.html")


@login_manager.user_loader
def load_user(user_id):
    db = SinoDB()
    user = db.get_user_by_id(user_id)
    if user:
        return User(user[0])
    else:
        return None


@app.route("/sino-type/admin-login", methods=['GET', 'POST'])
def adminloginpage():
    form = LoginForm()
    db = SinoDB()

    # If user submits the form: 
    if form.validate_on_submit():
        user = db.get_user_by_username(form.username.data)
        if user:
            user = User(user[0])
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for("adminportal"))
        else: 
            flash(f"Username or password is incorrect. Please try again.")
    
    # If form has not been submitted yet: 
    return render_template("adminlogin.html", form=form)


@app.route("/sino-type/admin-signup", methods=['GET', 'POST'])
def adminsignuppage():
    form = SignupForm()
    db = SinoDB()

    # If user submits the form:
    if form.validate_on_submit():
        # Check if passwords match
        if form.password.data != form.confirm_password.data:
            flash("Passwords do not match. Please try again.")
            return render_template("admin_signup.html", form=form)
        
        # Check if username already exists
        existing_user = db.get_user_by_username(form.username.data)
        if existing_user:
            flash("Username already exists. Please choose a different username.")
            return render_template("admin_signup.html", form=form)
        
        # Validation for the admin key
        try:
          master_key = db.get_master_key()
          if not bcrypt.check_password_hash(master_key, form.key.data):
            flash("Invalid admin key. Please try again.")
            return render_template("admin_signup.html", form=form)
        except Exception as e:
            flash("Error creating account. Please try again.")
            print(f"Signup error: {e}")

        
        try:
            # Hash the password and create the user
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.create_user(form.username.data, hashed_password)
            flash("Account created successfully! You can now log in.")
            return redirect(url_for("adminloginpage"))
        except Exception as e:
            flash("Error creating account. Please try again.")
            print(f"Signup error: {e}")
    
    # If form has not been submitted yet:
    return render_template("admin_signup.html", form=form)


@app.route("/sino-type/admin-portal", methods=["POST", "GET"])
@login_required
def adminportal():
    # This is if the user has submitted the database update form 
    if request.method == "POST":
        db = SinoDB()

        # Obtain the language to update, the hanzi, and the romanization
        language = request.form["language"].lower()
        hanzi = request.form["hanzi"] 
        roman = request.form["romanization"] 

        # Checks that the romanji input is all English characters 
        roman = roman.lower() 
        if (not checkRoman(roman)):
            flash(f"The romanji must consist entirely of Latin characters, no punctuation.")

        # Checks that the hanzi is actually hanzi 
        elif (not checkHanzi(hanzi)):
            flash(f"The hanzi you have entered is not a valid hanzi character.")

        # Checks if the entry already exists in the database. If so, let the admin know. 
        elif (checkEntryExistence(db, language, hanzi, roman)):
            flash(f"You have already added ({hanzi}, {roman}) to the {language} database.", "info")

        else:
            # TODO: store recently added entries so they can be deleted if there has been a mistake
            # session["database_entries"].append((hanzi, roman, language)) 
            # session.modified = True 
            
            # Update the corresponding table in database 
            db.create_translation_entry(language, hanzi, roman)

    return render_template("adminportal.html")


@app.route("/sino-type/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('adminloginpage'))


app.run(host="0.0.0.0", port=5000)
