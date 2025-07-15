from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user
import os
import requests

# Local imports
from clean_csvs import clean_csv_1, clean_csv_2, clean_3_4_combined
from typewanese_util import remove_recent_files, export_audio, get_options_tai
from sinodb import SinoDB
from forms import LoginForm, SignupForm
from user import User
from sinotype_utils import checkHanzi, checkRoman, checkEntryExistence
from taiping_utils import get_endings


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
app.secret_key = os.environ['APP_KEY']

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'adminloginpage'

@app.route("/", methods=["GET"])
def index():
  return redirect(url_for("home"))

## HOME
@app.route("/home", methods=["GET"])
def home():
  return render_template("home.html")

## BOBAWAY
@app.route("/app", methods=["GET", "POST"])
def bobaway():
  return render_template("index.html")

## ABOUT
@app.route("/about", methods=["GET"])
def about():
  return render_template("about.html")

## ROMANIZATION
@app.route("/romanization", methods=["GET"])
def romanization():
  return render_template("romanization.html")

## TYPEWANSE
@app.route("/typewanese", methods=["GET", "POST"])
def typewanese():
  if request.method == "POST":
    path = request.form.get("path")
    red = request.form.get("red")
    ogg = request.form.get("ogg")
    hour = remove_recent_files()

    if path == "typewanese-1":
        sorted_options, sorted_tai = get_options_tai(red, cleaned_2, cleaned_3_4, src_1_search, src_1_code, src_1_tai)
        export_audio(sorted_options, hour)
        return render_template("typewanese.html",
                                ogg=ogg,
                                red=red,
                                options=sorted_options,
                                tai=sorted_tai,
                                hour=hour)
    
    elif path == "typewanese-2":
        return render_template("typewanese.html",
                             ogg=ogg,
                             red="",
                             options=[],
                             tai=[],
                             hour=hour)
  
  return render_template("typewanese.html")


## TAI-PING
@app.route("/tai-ping", methods=["GET", "POST"])
def tai_ping():
  if request.method == "POST":
    path = request.form.get("path")
    full = request.form.get("full")
    page = request.form.get("page")
    change = request.form.get("change")
    og = request.form.get("og")
    ogg = request.form.get("ogg")
    filename = request.form.get("filename")
    prev = request.form.get("prev")
    last = request.form.get("last")
    slider = request.form.get("slider")
    hour = remove_recent_files()

    if full == 'True':
        split = ogg.split(" ")
        files = os.listdir("static/tai-sounds")
        for word in split:
            if f"{word}.wav" not in files:
                url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={word}"
                myfile = requests.get(url)
                open(f"static/tai-sounds/{word}.wav", "wb").write(myfile.content)

        return render_template("tai-ping.html",
                            og=og,
                            ogg=ogg,
                            change=change,
                            filename=filename,
                            page=page,
                            full=True,
                            files=len(split),
                            slider=slider)
    else:
        endings, data = get_endings(og, ogg, change, filename, page, prev, last)
        return render_template("tai-ping.html",
                            og=data["og"],
                            ogg=data["ogg"],
                            change=data["change"],
                            filename=data["filename"],
                            page=data["page"],
                            endings=endings,
                            prev=data["prev"],
                            last=data["last"],
                            full=True,
                            slider=slider)

  return render_template("tai-ping.html")


## SINO-TYPE
@app.route("/sino-type", methods=["GET"])
def sino_type():
  return render_template("sino-type.html")


# SINO-TYPE APIS
@app.route("/api/all-languages-data", methods=["GET"])
def get_all_languages_data():
    """Get data for all languages in the format expected by sino-type.js"""
    try:
        db = SinoDB()
        languages = ['shanghainese', 'korean', 'taiwanese', 'vietnamese']
        
        # Create the same structure as output.json
        all_data = {}
        
        for lang_index, language in enumerate(languages):
            entries = db.get_romanization_mapping(language)
            
            # Group by romanization
            for e in entries:
                roman = e[0]
                hanzi = e[1]
                if roman not in all_data:
                    all_data[roman] = [[], [], [], []]  # 4 empty arrays for 4 languages
                
                all_data[roman][lang_index] = hanzi
        
        return jsonify(all_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ADMIN PAGES
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


# ADMIN REQUESTS
@app.route("/sino-type/add-entry", methods=["POST"])
@login_required
def add_entry():
    db = SinoDB()
    # Get the single hanzi character
    hanzi = request.form["hanzi"]
    
    # Validate hanzi first
    if not checkHanzi(hanzi):
        flash(f"The hanzi you have entered is not a valid hanzi character.")
        return redirect(url_for("adminportal"))
    
    # Collect all language/romanization pairs
    romanization_pairs = []
    form_keys = list(request.form.keys())
    
    # Find all language/romanization pairs
    for key in form_keys:
        if key.startswith("language_"):
            index = key.split("_")[1]
            romanization_key = f"romanization_{index}"
            
            if romanization_key in request.form:
                language = request.form[key].lower()
                roman = request.form[romanization_key].lower()
                romanization_pairs.append((language, roman))
    
    # Process each romanization pair
    successful_additions = []
    errors = []
    
    for language, roman in romanization_pairs:
        # Validate romanization
        if not checkRoman(roman):
            errors.append(f"'{roman}' must consist entirely of Latin characters, no punctuation.")
            continue
            
        # Check if entry already exists
        if checkEntryExistence(db, language, hanzi, roman):
            errors.append(f"({hanzi}, {roman}) already exists in the {language} database.")
            continue
        
        # Try to add the entry
        try:
            db.create_translation_entry(language, hanzi, roman)
            successful_additions.append(f"({hanzi}, {roman}) added to {language}")
        except Exception as e:
            errors.append(f"Error adding ({hanzi}, {roman}) to {language}")
            print(f"Add error: {e}")
    
    # Flash results
    if successful_additions:
        flash(f"Successfully added: {', '.join(successful_additions)}", "info")
    
    if errors:
        for error in errors:
            flash(error)

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


# LOGIN MANAGEMENT
@app.route("/sino-type/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('adminloginpage'))


@login_manager.user_loader
def load_user(user_id):
    db = SinoDB()
    user = db.get_user_by_id(user_id)
    if user:
        return User(user[0])
    else:
        return None


# RUN
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
