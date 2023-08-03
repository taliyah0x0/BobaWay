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

exceptions = []
# Load in exceptions dictionary (普通話，國語，台語，Note，Alternative)
with open("exceptions.csv", "r") as csvfile:
    f = csv.reader(csvfile)
    first = True
    for row in f:
        if first == False:
            exceptions.append(row)
        else:
            first = False
exceptions = np.array(exceptions)


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
                        new_syll = syll[: syll.index(vowel)]
                        # Add the vowel with corrected tone indication
                        new_syll += vowel_tone[alph[0].index(vowel)][tone]
                        # Add the rest of the syllable
                        new_syll += syll[syll.index(vowel) + 1:]
                        corrected = True
                if corrected == False:  # Run the following if the vowel hasn't been corrected yet
                    if "o" in syll:  # Next in priority is 'o'
                        # Append first part of syllable up to 'o'
                        new_syll = syll[: syll.index("o")]
                        # Add the 'o' with the corrected tone indication
                        new_syll += vowel_tone[4][tone]
                        # Add the rest of the syllable
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
                            new_syll += syll[y + 1:]
                if corrected == False: # Run the following if the tone hasn't been corrected yet:
                    if "n" in syll:
                        # Append first part of syllable up to vowel
                        new_syll = syll[: syll.index("n")]
                        # Add the vowel with corrected tone indication
                        new_syll += vowel_tone[6][tone]
                        # Add the rest of the syllable
                        new_syll += syll[syll.index("n") + 1:]
                        corrected = True
                if corrected == False: # Run the following if the tone hasn't been corrected yet:
                    if "m" in syll:
                        # Append first part of syllable up to vowel
                        new_syll = syll[: syll.index("m")]
                        # Add the vowel with corrected tone indication
                        new_syll += vowel_tone[5][tone]
                        # Add the rest of the syllable
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

        if path == "0":
            en = request.form.get("en")
            cn = request.form.get("cn")
            color = request.form.get("color")

            mandarin = ""
            if en != None:
                mandarin = GoogleTranslator(source="auto", target="zh-TW").translate(en)
            else:
                mandarin = cn
                en = ""

            # Replace Chinese Mandarin words with Taiwanese Mandarin words
            for word in exceptions[:, 0]:
                if word != '':
                    if word in mandarin:
                        cn_split = mandarin.split(word)
                        cn_split[1:1] = exceptions[list(exceptions[:, 0]).index(word), 1]
                        mandarin = ''.join(cn_split)
            print(mandarin)

            browser = await pyppeteer.launcher.connect(browserWSEndpoint='wss://chrome.browserless.io?token='+'d2810faf-334d-4558-bdf3-c9a3765afe97')
            # c4943715-11be-48e8-a7fb-3b6536e4b8eb (23)
            # e4057a02-a262-4d88-9b37-c958c579719c (28)
            # ec16030a-7686-4132-9116-843d27126bc4 (31)
            # d2810faf-334d-4558-bdf3-c9a3765afe97 (01)
            page = await browser.newPage()

            # Using this Mandarin to Taiwanese translator
            await page.goto("http://tts001.iptcloud.net:8804/")

            # Type in the translated Mandarin phrase
            cn_input = ".reference-input"
            await page.waitForSelector(cn_input)
            await page.type(cn_input, mandarin)
            await page.waitFor(len(mandarin) * 50)

            # Click on the button to get romanization
            bt = "#js-translate"
            await page.waitForSelector(bt)
            await page.click(bt)
            await page.waitFor(len(mandarin) * 50)

            # Get the romanization
            selector = await page.querySelectorAll('#text1')
            valueSelector = await selector[0].getProperty("value")
            romanized = await valueSelector.jsonValue()

        elif path == "1":
            en = request.form.get("en")
            mandarin = GoogleTranslator(source="auto", target="zh-TW").translate(en)
            cn = request.form.get("cn")
            romanized = request.form.get("tw")

        words = romanized.split(' ')

        finals = []
        for word in words:
            finals.append(add_tones(word))
        romanized = " ".join(finals)

        cleaned = ''
        for letter in romanized:
            if letter != '1' and letter != '4' and letter != '6' and letter != '9':
                cleaned += letter
        romanized = cleaned
        print(romanized)

        toggle_note = False
        alternative = ""
        note = ""
        # Replace pronunciations
        for word in exceptions[:, 4]:
            if word != '':
                if word in romanized:
                    romanized_split = romanized.split(word)
                    romanized_split[1:1] = exceptions[list(exceptions[:, 4]).index(word), 2]
                    romanized = ''.join(romanized_split)
                    toggle_note = True
                    alternative = word
                    if exceptions[list(exceptions[:, 4]).index(word), 3] != '':
                        note = exceptions[list(exceptions[:, 4]).index(word), 3]

        # Turn on note if there is alternative available
        for word in exceptions[:, 2]:
            if word != '':
                if word in romanized:
                    if exceptions[list(exceptions[:, 2]).index(word), 3] != '':
                        toggle_note = True
                        note = exceptions[list(exceptions[:, 2]).index(word), 3]
                        if exceptions[list(exceptions[:, 2]).index(word), 4] != '':
                            alternative = exceptions[list(exceptions[:, 2]).index(word), 4]
        alternative = add_tones(alternative)

        print(note, alternative)
    
        key = random.randint(1, 10000)
        now = str(datetime.now())
        hour = now[11:13]
        files = os.listdir("static")
        for file in files:
            if file[-3:] == "wav":
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

        if path == "1":
            with open("exceptions.csv", 'a') as csvfile:
                filewriter = csv.writer(
                    csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                row = []
                row.append(mandarin)
                row.append(cn)
                row.append(romanized)
                row.append("")
                row.append("")
                filewriter.writerows([row])

        return render_template(
            "output.html",
            en=en,
            mandarin=mandarin,
            romanization=romanized,
            file_count=file_count,
            hour=hour,
            key=key,
            color=color,
            play=0,
            toggle_note=toggle_note,
            alternative=alternative,
            note=note,
        )
    return render_template("index.html")


app.run(host="0.0.0.0", port=81)
