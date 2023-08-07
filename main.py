from flask import Flask, request, render_template
from deep_translator import GoogleTranslator
import requests
import os
import random
from datetime import datetime
import pyppeteer
from pydub import AudioSegment
import csv
import numpy as np
import pinyin

num = ["1", "2", "3", "5", "7", "8"]
alph = [["a", "e"], ["o"], ["i", "u"], ["n"], ["m"]]  # Order of priority to add tone
# In order of 2, 3, 5, 7, 8
vowel_tone = [
    ["a", "á", "à", "â", "ā", "a̍"],
    ["e", "é", "è", "ê", "ē", "e̍"],
    ["i", "í", "ì", "î", "ī", "i̍"],
    ["u", "ú", "ù", "û", "ū", "u̍"],
    ["o", "ó", "ò", "ô", "ō", "o̍"],
    ["m", "ḿ", "m̀", "m̂", "m̄", "m̍"],
    ["n", "ń", "ǹ", "ň", "n̄", "n̍"],
]


def load_exceptions():
    exceptions = []
    # Load in exceptions dictionary (普通話，國語，台語，Note，Alternative, Yes (CN->TW), No (CN->TW), Yes (TW->RO), No (TW->RO))
    with open("exceptions.csv", "r") as csvfile:
        f = csv.reader(csvfile)
        for row in f:
            exceptions.append(row)
    exceptions = np.array(exceptions)
    return exceptions


def load_validation():
    exceptions = load_exceptions()
    high_priority = []
    other = []
    for row in exceptions:
        if int(row[-2]) / int(row[-1]) < 1 or int(row[-4]) / int(row[-3]) < 1:
            high_priority.append(row)
        elif int(row[-2]) / int(row[-1]) < 100 or int(row[-4]) / int(row[-3]) < 100:
            other.append(row)
    val_list = []
    if len(high_priority) != 0:
        pick_rand = random.randint(0, len(high_priority) - 1)
        val_list = [high_priority[pick_rand][0], high_priority[pick_rand][1], high_priority[pick_rand][2]]
    else:
        pick_rand = random.randint(0, len(other) - 1)
        val_list = [other[pick_rand][0], other[pick_rand][1], other[pick_rand][2]]
    
    val_list.append(list(exceptions[:, 0]).index(val_list[0]))
    
    return tuple(val_list)


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
    tone = 4  # Default tone is 8, which has no indication
    # Rewrite syllables with proper tone indication
    for syll in syllables:
        if syll != "":  # Skip blank syllables in list
            if syll[-1] in num:  # Check if there is a number at the end of the syllable
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
        print("path", path)

        if path == '3':
            return render_template("about.html")
        elif path == '4':
            return render_template("romanization.html")
        elif path == '5':
            cn, tw, ro, key = load_validation()
            return render_template("validation.html", cn=cn, tw=tw, ro=ro, key=key)
        elif path == '6':
            cn_tw = request.form.get("cn-tw")
            tw_ro = request.form.get("tw-ro")

            if cn_tw != '2' or tw_ro != '2':

                cn = request.form.get("cn")
                tw = request.form.get("tw")
                ro = request.form.get("ro")

                print(cn, cn_tw, tw_ro)
                exceptions = load_exceptions()

                with open("exceptions.csv", 'w') as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    for row in exceptions:
                        if row[0] == cn:
                            if cn_tw == '0':
                                row[-4] = str(int(row[-4]) + 1)
                            elif cn_tw == '1':
                                row[-3] = str(int(row[-3]) + 1)

                            if tw_ro == '0':
                                row[-2] = str(int(row[-2]) + 1)
                            elif tw_ro == '1':
                                row[-1] = str(int(row[-1]) + 1)
                        filewriter.writerows([row])
            return ('<script>window.close()</script>') # Turn it into a blank tab that closes itself
        elif path == '0' or path == '1' or path == '2':
            color = request.form.get("color")

            en = request.form.get("en")
            mandarin = GoogleTranslator(source="auto", target="zh-TW").translate(en)
            cn = request.form.get("cn")
            print("translate", mandarin)

            if path == "0":
                cn = mandarin

            elif path == "2":  # Edited the Taiwanese
                cn = request.form.get("cn")
                alternative = request.form.get("tw")
                romanized = request.form.get("ro")

            exceptions = load_exceptions()

            if path == "0" or path == "1":  # Regular Translation or only edited Mandarin

                # Replace Chinese Mandarin words with Taiwanese Mandarin words
                for word in exceptions[:, 0]:
                    if word in cn and int(exceptions[list(exceptions[:, 0]).index(word), 5])/int(exceptions[list(exceptions[:, 0]).index(word), 6]) >= 1:
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

                browser = await pyppeteer.launcher.connect(browserWSEndpoint='wss://chrome.browserless.io?token=' + 'c4943715-11be-48e8-a7fb-3b6536e4b8eb')
                page = await browser.newPage()

                # Using this Mandarin to Taiwanese translator
                await page.goto("http://tts001.iptcloud.net:8804/")

                # Type in the translated Mandarin phrase
                cn_input = ".reference-input"
                await page.waitForSelector(cn_input)
                await page.type(cn_input, cn)
                await page.waitFor(len(cn) * 50)

                # Click on the button to get romanization
                bt = "#js-translate"
                await page.waitForSelector(bt)
                await page.click(bt)
                await page.waitFor(len(cn) * 250)

                # Get the romanization
                selector = await page.querySelectorAll('#text1')
                valueSelector = await selector[0].getProperty("value")
                romanized = await valueSelector.jsonValue()
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

            if (path == "1" and mandarin != cn) or (path == "2" and romanized != alternative):
                with open("exceptions.csv", 'a') as csvfile:
                    filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    row = []
                    if path == "1":
                        row.append(mandarin)  # Original English to Mandarin Translation
                        row.append(cn)  # Corrected Translation
                        row.append(romanized)
                        row.append("")
                        row.append("")
                        row.append(0)  # Start with 0 Yes for Mandarin to Taiwanese Mandarin
                        row.append(2)  # Start with 2 No for Mandarin to Taiwanese Mandarin
                        row.append(0)
                        row.append(2)
                    if path == "2":
                        row.append(mandarin)  # Original English to Mandarin Translation
                        row.append(cn)  # Corrected Translation
                        row.append(romanized)  # Corrected Taiwanese
                        row.append("")
                        row.append(alternative)  # Original Taiwanese
                        row.append(0)
                        row.append(2)
                        row.append(0)
                        row.append(2)
                    filewriter.writerows([row])

                exceptions = load_exceptions()

                exc_list = [mandarin, cn, romanized]
                exc_key = len(exceptions[:, 0])
                for i in range(3):
                    if i != 2:
                        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={exc_list[i]}.&tl=zh-TW&total=1&idx=0&textlen=15&tk=350535.255567&client=webapp&prev=input"
                    else:
                        url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={exc_list[i]}"
                    myfile = requests.get(url)
                    open(f"static/exc_{exc_key}_{i}.wav", "wb").write(myfile.content)

            toggle_note = False
            note = ""
            # Replace pronunciations
            for word in exceptions[:, 4]:
                if word != '' and int(exceptions[list(exceptions[:, 4]).index(word), 7])/int(exceptions[list(exceptions[:, 4]).index(word), 8]) >= 1:
                    if word in romanized:
                        romanized_split = romanized.split(word)
                        romanized_split[1:1] = exceptions[list(exceptions[:, 4]).index(word), 2]
                        romanized = ''.join(romanized_split)

            # Turn on note if there is alternative or note available
            for word in exceptions[:, 2]:
                if word in romanized:
                    if exceptions[list(exceptions[:, 2]).index(word), 3] != '':
                        toggle_note = True
                        note += exceptions[list(exceptions[:, 2]).index(word), 3]
                    if exceptions[list(exceptions[:, 2]).index(word), 4] != '' and int(exceptions[list(exceptions[:, 2]).index(word), 7])/int(exceptions[list(exceptions[:, 2]).index(word), 8]) < 100 and int(exceptions[list(exceptions[:, 2]).index(word), 7])/int(exceptions[list(exceptions[:, 2]).index(word), 8]) >= 1:
                        alternative = exceptions[list(exceptions[:, 2]).index(word), 4]
                        alternative = add_tones(alternative)
                        note += "\n Alternative for " + word + "→ " + alternative
                        toggle_note = True

            print(note, alternative)

            key = random.randint(1, 10000)
            now = str(datetime.now())
            hour = now[11:13]
            files = os.listdir("static")
            for file in files:
                if file[-3:] == "wav" and file[0:3] != "exc":
                    if int(file[0:2]) <= int(hour) - 1 or int(file[0:2]) > int(hour):  # Remove files from 1 hour ago
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
    return render_template("index.html")


app.run(host="0.0.0.0", port=81)

# yapf main.py --style='{column_limit: 200}' -i