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

db = SinoDB()


@app.route("/", methods=["GET", "POST"])
async def gfg():
  if request.method == "POST":
    path = request.form.get("path")
    color = request.form.get("color")
    red = request.form.get("red")
    full = request.form.get("full")
    page = request.form.get("page")
    change = request.form.get("change")
    og = request.form.get("og")
    ogg = request.form.get("ogg")
    filename = request.form.get("filename")
    prev = request.form.get("prev")
    last = request.form.get("last")
    slider = request.form.get("slider")
    print("path", path)

    now = str(datetime.now())
    hour = now[11:13]
    files = os.listdir("static/sounds")
    for file in files:
      if file[-3:] == "wav":
        if int(file[0:2]) <= int(hour) - 1 or int(
            file[0:2]) > int(hour):  # Remove files from 1 hour ago
          os.remove(f"static/sounds/{file}")

    if path == '3':
      return render_template("about.html")
    elif path == '4':
      return render_template("romanization.html")
    elif path == '7':
      return render_template("tai-ping.html")
    elif path == '8':
      return render_template("typewanese.html")
    elif path == '9':
      return render_template("index.html")
    elif path == '0' or path == '1' or path == '2':
      color = request.form.get("color")

      en = request.form.get("en")
      mandarin = GoogleTranslator(source="auto", target="zh-TW").translate(en)
      cn = request.form.get("cn")
      romanized = ""
      alternative = ""
      py = ""
      print("translate", mandarin)

      if path == "0":
        cn = mandarin

      exceptions = load_exceptions()

      if path == "0" or path == "1":  # Regular Translation or only edited Mandarin
        # Replace Chinese Mandarin words with Taiwanese Mandarin words
        '''for word in exceptions[:, 0]:
          if word in cn:
            cn_split = cn.split(word)
            cn_split[1:1] = exceptions[list(exceptions[:, 0]).index(word), 1]
            cn = ''.join(cn_split)
        print(cn)'''

        # Get Pinyin
        spaced = ""
        for char in cn:
          spaced += char
          spaced += " "
        py = pinyin.get(spaced)
        print(py)

        #page = requests.get(f"http://tts001.iptcloud.net:8804/display?text0={cn}")
        #romanized = BeautifulSoup(page.content, "html.parser")
        '''while len(cn) > 0:
          found = False
          temp_cn = cn[:]
          while not found:
            for s_list in src_1_search:
              for search_term in s_list:
                if search_term == temp_cn:
                  romanized += src_1_code[src_1_search.index(s_list)] + " "
                  new_cn += search_term #src_1_tai[src_1_search.index(s_list)]
                  cn = cn[len(search_term):]
                  found = True
                  temp_cn = ""
                  print(romanized, search_term, s_list)
            temp_cn = temp_cn[:-1]
        print(romanized)'''

        browser = await pyppeteer.launcher.connect(
            browserWSEndpoint='wss://chrome.browserless.io?token=' + 'e4057a02-a262-4d88-9b37-c958c579719c')
        page = await browser.newPage()

        # Using this Mandarin to Taiwanese translator
        await page.goto("https://camplingo.com/translate?stlang=nan")

        # Click on the button to bring up english input
        translate_en = ".css-1fs5cst"
        await page.waitForSelector(translate_en)
        await page.click(translate_en)

        # Enter in the input box
        text_input = ".css-1kp110w"
        await page.waitForSelector(text_input)
        await page.type(text_input, en)

        bt = ".css-f2hjvb"
        await page.waitForSelector(bt)
        await page.click(bt)
        await page.waitFor(200)

        word_bt = ".token"
        await page.waitForSelector(word_bt)

        first_block = await page.querySelectorAll(".annotated_study_tokens")
        elements = await first_block[0].querySelectorAll(word_bt)
        print(len(elements))

        index = 0
        while index < len(elements):
          await page.waitForSelector(f'{word_bt}:nth-child({index + 1})', {'visible': True})
          first_block = await page.querySelectorAll(".annotated_study_tokens")
          elements = await first_block[0].querySelectorAll(word_bt)
          has_class = await page.evaluate('(element) => element.classList.contains("is_word")', elements[index])
          if has_class:
            await elements[index].click()
            await page.evaluate('(element) => element.click()', elements[index])
            await page.click(".token:nth-of-type({})".format(index + 1))
            print("has")
            await page.waitForSelector(".phonetic_aide")

            first_block = await page.querySelectorAll(".annotated_study_tokens")
            elements = await first_block[0].querySelectorAll(word_bt)
            child = await elements[index].querySelector('.css-0')

            grandchild = await child.querySelector('.phonetic_aide')
            inner_html = await page.evaluate('(element) => element.innerHTML', grandchild)
            if 'ⁿ' in inner_html:
              inner_html = inner_html.replace('ⁿ', '')
            romanized += inner_html + " "
            print(romanized)
          else:
            print("else")
            first_block = await page.querySelectorAll(".annotated_study_tokens")
            elements = await first_block[0].querySelectorAll(word_bt)
            child = await elements[index].querySelector('.css-0')
            grandchild = await child.querySelector('.text')
            inner_html = await page.evaluate('(element) => element.innerHTML', grandchild)

            if not bool(re.search(r'[^\w\s]', inner_html)):
              found = False
              counter = 0
              while not found:
                s_list = src_1_search[counter]
                if inner_html in s_list:
                  romanized += src_1_code[src_1_search.index(s_list)] + " "
                  found = True
                counter += 1
            else:
              romanized += inner_html;
          index += 1
      '''cleaned = ''
      for letter in romanized:
        if letter != '4' and letter != '6' and letter != '9' and letter != '.' and letter != '?' and letter != '!':
          cleaned += letter
      romanized = cleaned'''

      words = romanized.split(' ')
      '''finals = []
      for word in words:
        finals.append(add_tones(word))
      romanized = " ".join(finals)'''

      print(words)

      toggle_note = False
      note = ""
      # Replace pronunciations
      for word in exceptions[:, 4]:
        if word != '' and exceptions[list(exceptions[:, 4]).index(word),
                                     2] in romanized:
          romanized_split = romanized.split(
              exceptions[list(exceptions[:, 4]).index(word), 2])
          romanized_split[1:1] = word
          romanized = ''.join(romanized_split)

      # Turn on note if there is alternative or note available
      for word in exceptions[:, 2]:
        if word in romanized:
          if exceptions[list(exceptions[:, 2]).index(word), 3] != '':
            toggle_note = True
            note += exceptions[list(exceptions[:, 2]).index(word), 3]
          if exceptions[list(exceptions[:, 2]).index(word), 4] != '':
            alternative = exceptions[list(exceptions[:, 2]).index(word), 4]
            alternative = add_tones(alternative)
            note += '\n Alternative for "' + alternative + '" → ' + word
            toggle_note = True

      print(note, alternative)

      words = romanized.split(' ')

      key = random.randint(1, 10000)
      now = str(datetime.now())
      hour = now[11:13]
      files = os.listdir("static")
      for file in files:
        if file[-3:] == "wav":
          if int(file[0:2]) <= int(hour) - 1 or int(
              file[0:2]) > int(hour):  # Remove files from 1 hour ago
            os.remove(f"static/{file}")

      file_count = 0
      for count in range(len(words) -
                         1):  # extra space of words for some reason
        search_input = words[count]
        if search_input[-2:] == 'a̍':
          search_input = search_input[:-2] + 'ah'
        elif search_input[-2:] == 'āh':
          search_input = search_input[:-2] + 'á'
        url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={search_input}"
        myfile = requests.get(url)
        print(search_input)
        open(f"static/{hour}_{key}_{count}.wav", "wb").write(myfile.content)

        # Trim first 0.3 and last 0.4 seconds
        song = AudioSegment.from_mp3(f"static/{hour}_{key}_{count}.wav")
        trimmed = song[300:-400]
        trimmed.export(f"static/{hour}_{key}_{count}.wav", format="wav")
        file_count += 1

      return render_template(
          "output.html",
          en=en,
          mandarin=cn,
          romanization=romanized,
          file_count=file_count,
          hour=hour,
          key=key,
          color=color,
          play=0,
          toggle_note=toggle_note,
          note=note,
          pinyin=py,
      )
    elif path == '10':
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
        endings = []
        if filename != "":
          if filename[-1] in num:
            if filename[:-1] in consonants:
              filename = filename[:-1] + "a" + filename[-1]
          else:
            if filename in consonants:
              filename += "a"

          temp_tone = add_tones(filename)
          print(og, '*', change, '*', temp_tone, '*', filename)
          temp = ""
          temp2 = ""
          if change != '' and len(og) > 1 and og[-1] == 'h':
            for i in range(len(og) - 1):
              temp += temp_tone[i]
          else:
            for i in range(len(og)):
              temp += temp_tone[i]
          for i in range(len(temp), len(temp) + len(change)):
            try:
              temp2 += temp_tone[i]
            except:
              pass
          if filename[-1] == '4':
            if (og != '' and temp2 == '') or temp2 != '':
              if (og != '' and temp2 == '') and og[-1] not in consonants:
                temp2 += 'h'
              elif temp2 != '' and temp2[-1] not in consonants:
                temp2 += 'h'
          og = temp
          change = temp2
          print(og, '*', change, '*', temp_tone, '*', filename)

          if filename != "":
            files = os.listdir("static/tai-sounds")
            if f"{filename}.wav" not in files:
              url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={temp_tone}"
              myfile = requests.get(url)
              open(f"static/tai-sounds/{filename}.wav",
                   "wb").write(myfile.content)

              # Trim first 0.3 and last 0.4 seconds
              song = AudioSegment.from_file(
                  file=f"static/tai-sounds/{filename}.wav", format="wav")
              trimmed = song[300:-400]
              trimmed.export(out_f=f"static/tai-sounds/{filename}.wav",
                             format="wav")

            if page == '1' and og[-1] in vowels:
              page = '2'

            if page == '2' and filename[-1] == '4':
              page = '3'

            endings = []
            if page == '2':
              last = ""
              if filename[-1] not in num:
                if filename[-1] == '4':
                  last = og[-2]
                else:
                  last = og[-1]
              else:
                if change == '':
                  last = filename[-2]
                else:
                  last = filename[-3]
              try:
                endings = match_lett[vowels.index(last)]
              except:
                ogg += temp_tone + " "
                og = ""
                page = '0'
                last = ""
                prev = ""
                filename = ""

            if page == '3' or page == '4':
              if page == '3':
                ogg += temp_tone + " "
              else:
                ogg += temp_tone + "-"
              change = ""
              og = ""
              page = '0'
              last = ""
              prev = ""
              filename = ""

      return render_template("tai-ping.html",
                             og=og,
                             ogg=ogg,
                             change=change,
                             filename=filename,
                             page=page,
                             endings=endings,
                             prev=prev,
                             last=last,
                             full=False,
                             slider=slider)
    elif path == '11':
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
    elif path == '12':
      return render_template("typewanese.html",
                             ogg=ogg,
                             red="",
                             options=[],
                             tai=[],
                             hour=hour)
  return render_template("index.html")


@app.route("/sino-type", methods=["GET", "POST"])
def sino_type():
  return render_template("sino-type.html")


@login_manager.user_loader
def load_user(user_id): 
    user = db.get_user_by_id(user_id)
    if user:
        return User(user[0])
    else:
        return None


@app.route("/sino-type/admin-login", methods=['GET', 'POST'])
def adminloginpage():
    form = LoginForm()

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

        # Obtain the language to update, the hanzi, and the romanization
        language = request.form["language"]
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
        elif (checkEntryExistence(language, hanzi, roman)):
            flash(f"You have already added ({hanzi}, {roman}) to the {language} database.", "info")

        else:
            pass
            # TODO: store recently added entries so they can be deleted if there has been a mistake
            # session["database_entries"].append((hanzi, roman, language)) 
            # session.modified = True 
            
            # Update the corresponding table in database 
            # db.update_entry(language, hanzi, roman)

    return render_template("adminportal.html")
    

app.run(host="0.0.0.0", port=81)

# yapf main.py --style='{column_limit: 200}' -i
