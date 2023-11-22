from flask import Flask, request, render_template
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

num = ["1", "2", "3", "5", "7", "8"]
alph = [["a", "e"], ["o"], ["i", "u"], ["n"],
        ["m"]]  # Order of priority to add tone
# In order of 1, 2, 3, 5, 7, 8
vowel_tone = [
  ["a", "á", "à", "â", "ā", "a̍"],
  ["e", "é", "è", "ê", "ē", "e̍"],
  ["i", "í", "ì", "î", "ī", "i̍"],
  ["u", "ú", "ù", "û", "ū", "u̍"],
  ["o", "ó", "ò", "ô", "ō", "o̍"],
  ["m", "ḿ", "m̀", "m̂", "m̄", "m̍"],
  ["n", "ń", "ǹ", "ň", "n̄", "n̍"],
]

consonants = [
  'p', 'ts', 't', 'ph', 'tsh', 'th', 'k', 'ch', 's', 'kh', 'chh', 'j', 'b',
  'l', 'd', 'g', 'h', 'n'
]

vowels = ['a', 'e', 'i', 'o', 'u']
match_lett = [['i', 'u', 'p', 'm', 't', 'k', 'nn', 'ng', 'un', 'in'],
              ['k', 'nn', 'ng'],
              ['a', 'o', 'u', 'p', 'm', 't', 'nn', 'an', 'on'],
              ['a', 'e', 'o', 'u', 'p', 'm', 'k', 'ng', 'un', 'an'],
              ['i', 't', 'nn', 'an', 'in']]

# Read and clean source 1
csv_data_1 = []
with open("./static/src_1.csv", "r") as csvfile:
  f = csv.reader(csvfile)
  next(f, None)
  for row in f:
    # Columns C (Mandarin search terms), E (Taiwanese Romanization), and D (Taiwanese Characters) will be used
    csv_data_1.append([row[2], row[4], row[3]])

cleaned_1 = []
for x in range(len(csv_data_1)):
  cleaned_1.append([])  # Create a new row
  # Separate search terms (Example: ;一定;確定;)
  split = csv_data_1[x][0].split(";")
  # Remove extra space
  split.pop(0)
  split.pop(-1)
  cleaned_1[x].append(split)  # Final is [一定, 確定]

  # Separate syllables in romanization (Example: khak-teng7)
  syllables = csv_data_1[x][1].split("-")

  # Sometimes syllables are split with space instead of hyphen
  for syll in syllables:
    space_split = syll.split(" ")
    ind = syllables.index(syll)
    syllables.pop(ind)  # Remove incorrect syllable
    syllables[ind:ind] = space_split  # Insert corrected syllables

  new_syllables = []
  tone = 4  # Default tone is 8, which has no indication
  # Rewrite syllables with proper tone indication
  for syll in syllables:
    if syll != "":  # Skip blank syllables in list
      if syll[
          -1] in num:  # Check if there is a number at the end of the syllable
        tone = num.index(syll[-1])  # Map tone number to index number
        # Append first part of syllable without number at the end
        syll = syll[:-1]
      new_syll = syll
      corrected = False
      for vowel in alph[0]:
        if vowel in syll:  # Check if there is an a or e
          # Append first part of syllable up to vowel
          new_syll = syll[:syll.index(vowel)]
          # Add the vowel with corrected tone indication
          new_syll += vowel_tone[alph[0].index(vowel)][tone]
          # Add the rest of the syllable if vowel is not the last letter
          if len(syll) != len(new_syll):
            new_syll += syll[syll.index(vowel) + 1:]
          corrected = True
      if corrected == False:  # Run the following if the vowel hasn't been corrected yet
        if "o" in syll:  # Next in priority is 'o'
          # Append first part of syllable up to 'o'
          new_syll = syll[:syll.index("o")]
          # Add the 'o' with the corrected tone indication
          new_syll += vowel_tone[4][tone]
          if len(syll) != len(new_syll):
            # Add the rest of the syllable if 'o' is not the last letter
            new_syll += syll[syll.index("o") + 1:]
          corrected = True
      if corrected == False:  # Run the following if the vowel hasn't been corrected yet
        # Look for the last i or u
        for y in range(-1, -len(syll), -1):
          if syll[y] in alph[1]:
            new_syll = syll[:y]
            new_syll += vowel_tone[alph[1].index(syll[y]) + 2][tone]
            if len(syll) != len(new_syll):
              new_syll += syll[y + 1:]
      if new_syll[-1] == "N":  # Replace uppercase N with nn
        new_syll = new_syll[:-1]
        new_syll += "nn"
      new_syllables.append(new_syll)
  final_rev = "-".join(new_syllables)  # Rejoin syllables with hyphens
  # Add fixed romanization to second column in row
  cleaned_1[x].append(final_rev)
  cleaned_1[x].append(csv_data_1[x][2])

# Create 2 lists for search terms vs. romanization
src_1_search = []
src_1_code = []
src_1_tai = []
for row in cleaned_1:
  src_1_search.append(row[0])
  src_1_code.append(row[1])
  src_1_tai.append(row[2])

# Function for checking if the mandarin translation exists as a search term in source 1


def search_csv_1(text):
  for s_list in src_1_search:
    for search_term in s_list:
      if text == search_term:
        return True
  return False


# Read and clean source 2
csv_data_2 = []
with open("./static/src_2.csv", "r") as csvfile:
  f = csv.reader(csvfile)
  next(f, None)
  for row in f:
    cleanx = ""
    for char in row[3]:
      if ord(char) != 781:
        cleanx += char
    # Using columns for 華語, 台語, 備存對照, and 台羅
    csv_data_2.append([row[1], row[2], row[4], cleanx])
# Turn into numpy array to slice columns easier
cleaned_2 = np.array(csv_data_2)

# Read and clean source 3
csv_data_3 = []
with open("./static/src_3.csv") as csvfile:
  f = csv.reader(csvfile)
  next(f, None)
  for row in f:
    csv_data_3.append([row[2], row[3]])  # Using columns for 華語 and 漢字
cleaned_3 = []
# Some romanization have space instead of hyphen to separate, so fixing this with code below:
for x in range(len(csv_data_3)):
  cleaned_3.append([csv_data_3[x][0]])
  syllables = csv_data_3[x][1].split("-")
  for syll in syllables:
    space_split = syll.split(" ")
    ind = syllables.index(syll)
    syllables.pop(ind)
    syllables[ind:ind] = space_split
  final_rev = "-".join(syllables)
  cleaned_3[x].append(final_rev)

# Read and clean source 4
csv_data_4 = []
counter = 0
with open("./static/src_4.csv") as csvfile:
  f = csv.reader(csvfile)
  rows = []
  for row in f:
    rows.append(row)
  grab_set = rows[0][5:]
  for x in range(len(grab_set)):
    if counter == 0:
      csv_data_4.append([grab_set[x], grab_set[x + 1]])
    if counter == 3:
      counter = -1
    counter += 1
cleaned_4 = []
# Some romanization have space instead of hyphen to separate, so fixing this with code below:
for x in range(len(csv_data_4)):
  cleaned_4.append([csv_data_4[x][0]])
  syllables = csv_data_4[x][1].split("-")
  for syll in syllables:
    space_split = syll.split(" ")
    ind = syllables.index(syll)
    syllables.pop(ind)
    syllables[ind:ind] = space_split
  final_rev = "-".join(syllables)
  cleaned_4[x].append(final_rev)

# Combine sources 3 and 4 because of similar format and priority
cleaned_3_4 = cleaned_3 + cleaned_4
# Turn into numpy array to slice columns easier
cleaned_3_4 = np.array(cleaned_3_4)


def load_exceptions():
  exceptions = []
  # Load in exceptions dictionary (普通話，國語，台語，Note，Alternative)
  with open("exceptions.csv", "r") as csvfile:
    f = csv.reader(csvfile)
    for row in f:
      exceptions.append(row)
  exceptions = np.array(exceptions)
  return exceptions

def remove_comma(word):
  if "," in word:
    split = word.split(",")
    word = "/".join(split)
  return word


def add_tones(word):
  # Separate syllables in romanization (Example: khak-teng7)
  syllables = word.split("-")

  # Sometimes syllables are split with space instead of hyphen
  for syll in syllables:
    space_split = syll.split(" ")
    ind = syllables.index(syll)
    syllables.pop(ind)  # Remove incorrect syllable
    syllables[ind:ind] = space_split  # Insert corrected syllables

  new_syllables = []
  tone = 1  # Default tone is 1, which has no indication
  # Rewrite syllables with proper tone indication
  for syll in syllables:
    if syll != "":  # Skip blank syllables in list
      if syll[
          -1] in num:  # Check if there is a number at the end of the syllable
        tone = num.index(syll[-1])  # Map tone number to index number
        # Append first part of syllable without number at the end
        syll = syll[:-1]
        new_syll = syll
        corrected = False
        for vowel in alph[0]:
          if vowel in syll:  # Check if there is an a or e
            # Append first part of syllable up to vowel
            new_syll = syll[:syll.index(vowel)]
            # Add the vowel with corrected tone indication
            new_syll += vowel_tone[alph[0].index(vowel)][tone]
            # Add the rest of the syllable
            if syll.index(vowel) != -1:
              new_syll += syll[syll.index(vowel) + 1:]
            corrected = True
        if corrected == False:  # Run the following if the vowel hasn't been corrected yet
          if "o" in syll:  # Next in priority is 'o'
            # Append first part of syllable up to 'o'
            new_syll = syll[:syll.index("o")]
            # Add the 'o' with the corrected tone indication
            new_syll += vowel_tone[4][tone]
            # Add the rest of the syllable
            if syll.index("o") != -1:
              new_syll += syll[syll.index("o") + 1:]
            corrected = True
        if corrected == False:  # Run the following if the vowel hasn't been corrected yet
          # Look for the last i or u
          for y in range(-1, -len(syll), -1):
            if syll[y] in alph[2]:
              # Append first part of syllable up to vowel
              new_syll = syll[:y]
              # Add the vowel with corrected tone indication
              new_syll += vowel_tone[alph[2].index(syll[y]) + 2][tone]
              # Add the rest of the syllable
              if y != -1:
                new_syll += syll[y + 1:]
              corrected = True
        if corrected == False:  # Run the following if the tone hasn't been corrected yet:
          if "n" in syll:
            # Append first part of syllable up to vowel
            new_syll = syll[:syll.index("n")]
            # Add the vowel with corrected tone indication
            new_syll += vowel_tone[6][tone]
            # Add the rest of the syllable
            if syll.index("n") != -1:
              new_syll += syll[syll.index("n") + 1:]
            corrected = True
        if corrected == False:  # Run the following if the tone hasn't been corrected yet:
          if "m" in syll:
            # Append first part of syllable up to vowel
            new_syll = syll[:syll.index("m")]
            # Add the vowel with corrected tone indication
            new_syll += vowel_tone[5][tone]
            # Add the rest of the syllable
            if syll.index("m") != -1:
              new_syll += syll[syll.index("m") + 1:]
            corrected = True
        syll = new_syll
      if syll[-1] == '4':
        syll = syll[:-1]
        if syll[-1] not in consonants:
          syll += 'h'
      if syll[-1] == "N":  # Replace uppercase N with nn
        syll = syll[:-1]
        syll += "nn"
      new_syllables.append(syll)
  return ("-".join(new_syllables))  # Rejoin syllables with hyphens


app = Flask(__name__)


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
      print("translate", mandarin)

      if path == "0":
        cn = mandarin

      exceptions = load_exceptions()

      if path == "0" or path == "1":  # Regular Translation or only edited Mandarin
        # Replace Chinese Mandarin words with Taiwanese Mandarin words
        for word in exceptions[:, 0]:
          if word in cn:
            cn_split = cn.split(word)
            cn_split[1:1] = exceptions[list(exceptions[:, 0]).index(word), 1]
            cn = ''.join(cn_split)
        print(cn)

        # Get Pinyin
        spaced = ""
        for char in cn:
          spaced += char
          spaced += " "
        py = pinyin.get(spaced)
        print(py)

        page = requests.get(
          f"http://tts001.iptcloud.net:8804/display?text0={cn}")
        romanized = BeautifulSoup(page.content, "html.parser")
        print(romanized)

        alternative = ""

      cleaned = ''
      for letter in romanized:
        if letter != '4' and letter != '6' and letter != '9' and letter != '.' and letter != '?' and letter != '!':
          cleaned += letter
      romanized = cleaned

      words = romanized.split(' ')

      finals = []
      for word in words:
        finals.append(add_tones(word))
      romanized = " ".join(finals)

      print(romanized)
      
      toggle_note = False
      note = ""
      # Replace pronunciations
      for word in exceptions[:, 4]:
        if word != '' and exceptions[list(exceptions[:, 4]).index(word),2] in romanized:
          romanized_split = romanized.split(exceptions[list(exceptions[:, 4]).index(word),2])
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
      for count in range(len(words)):
        url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={words[count]}"
        myfile = requests.get(url)
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


app.run(host="0.0.0.0", port=81)

# yapf main.py --style='{column_limit: 200}' -i
