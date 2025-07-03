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


@app.route("/typewanese", methods=["GET", "POST"])
def typewanese():
  if request.method == "POST":
    red = request.form["red"]
    mandarin = GoogleTranslator(source="auto", target="zh-TW").translate(red)
    print(mandarin)

    options = []
    tai = []
    if mandarin in cleaned_2[:, 0]:
        selector = np.array([mandarin == s for s in cleaned_2[:, 0].flat
                             ]).reshape(cleaned_2[:, 0].shape)
        match = cleaned_2[selector]
        romanized = list(match[:, 3])
        for word in romanized:
          options.append(word)
          tai.append(list(match[:, 0])[romanized.index(word)])

    if mandarin in cleaned_3_4[:, 0]:
        selector = np.array([
            mandarin in s for s in cleaned_3_4[:, 0].flat
        ]).reshape(
            cleaned_3_4[:, 0].shape
        )  # Get location of all rows that have search term matching Mandarin exactly
        match = cleaned_3_4[selector]  # Select the rows
        romanized = list(match[:, 1])
        for word in romanized:
          options.append(word)
          tai.append(list(match[:, 0])[romanized.index(word)])

    match = []
    for s_list in src_1_search:
        for search_term in s_list:
          if mandarin == search_term:
            match.append(src_1_code[src_1_search.index(s_list)])
            tai.append(src_1_tai[src_1_search.index(s_list)])
    options += match

    sorted_options = []
    sorted_tai = []
    for x in range(len(options)):
        if options[x] not in sorted_options:
          sorted_options.append(options[x])
          sorted_tai.append(tai[x])

    for x in range(len(sorted_options)):
        url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={sorted_options[x]}"
        myfile = requests.get(url)
        open(f"static/sounds/{hour}_{sorted_options[x]}.wav",
             "wb").write(myfile.content)

        # Trim first 0.3 and last 0.4 seconds
        song = AudioSegment.from_mp3(
            f"static/sounds/{hour}_{sorted_options[x]}.wav")
        trimmed = song[300:-400]
        trimmed.export(f"static/sounds/{hour}_{sorted_options[x]}.wav",
                       format="wav")

    return render_template("typewanese.html",
                             ogg=ogg,
                             red=red,
                             options=sorted_options,
                             tai=sorted_tai,
                             hour=hour)
  else:
    return render_template("typewanese.html")


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
    db = SinoDB()
    # Fetch all entries from the database
    shanghainese = db.fetch_all_entries("shanghainese")
    korean = db.fetch_all_entries("korean")
    taiwanese = db.fetch_all_entries("taiwanese")
    vietnamese = db.fetch_all_entries("vietnamese")

    return render_template("adminportal.html", shanghainese=shanghainese, korean=korean, taiwanese=taiwanese, vietnamese=vietnamese)


@app.route("/sino-type/add-entry", methods=["POST"])
@login_required
def add_entry():
    db = SinoDB()
    # Obtain the language to update, the hanzi, and the romanization
    language = request.form["language"].lower()
    hanzi = request.form["hanzi"] 
    roman = request.form["romanization"].lower()

    # Checks that the romanji input is all English characters 
    if (not checkRoman(roman)):
        flash(f"The romanji must consist entirely of Latin characters, no punctuation.")
    elif (not checkHanzi(hanzi)):
        flash(f"The hanzi you have entered is not a valid hanzi character.")
    elif (checkEntryExistence(db, language, hanzi, roman)):
        flash(f"You have already added ({hanzi}, {roman}) to the {language} database.", "info")

    else:
        # Update the corresponding table in database
        try:
            db.create_translation_entry(language, hanzi, roman)
            flash(f"You have added ({hanzi}, {roman}) to the {language} database.", "info")
        except Exception as e:
            flash(f"Error adding entry. Please try again.")
            print(f"Add error: {e}")

    return redirect(url_for("adminportal"))


@app.route("/sino-type/delete-entry", methods=["POST"])
@login_required
def delete_entry():
    db = SinoDB()
    language = request.form["language"].lower()
    hanzi = request.form["hanzi"]
    roman = request.form["romanization"].lower()
    
    try:
        db.delete_translation_entry(language, hanzi, roman)
        flash(f"You have deleted ({hanzi}, {roman}) from the {language} database.", "info")
    except Exception as e:
        flash(f"Error deleting entry. Please try again.")
        print(f"Delete error: {e}")

    return redirect(url_for("adminportal"))


@app.route("/sino-type/update-entry", methods=["POST"])
@login_required
def update_entry():
    db = SinoDB()
    language = request.form["language"].lower()
    hanzi = request.form["hanzi"]
    original_roman = request.form["original_roman"].lower()
    new_roman = request.form["new_roman"].lower()

    if not checkRoman(new_roman):
        flash("The romanji must consist entirely of Latin characters, no punctuation.")
    elif checkEntryExistence(db, language, hanzi, new_roman):
        flash(f"You have already added ({hanzi}, {new_roman}) to the {language} database. Try deleting this entry or choosing a different romanization.", "info")
    else:
        try:
            db.update_translation_entry(language, hanzi, original_roman, new_roman)
            flash(f"You have updated ({hanzi}, {original_roman}) to ({hanzi}, {new_roman}) in the {language} database.", "info")
        except Exception as e:
            flash(f"Error updating entry. Please try again.")
            print(f"Update error: {e}")

    return redirect(url_for("adminportal"))


@app.route("/sino-type/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('adminloginpage'))


app.run(host="0.0.0.0", port=5000)
