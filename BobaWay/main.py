from flask import Flask, request, render_template
import pinyin
from deep_translator import GoogleTranslator
import requests
import os
import csv
import numpy as np
import random
from datetime import datetime

# Read and clean source 1
csv_data_1 = []
with open("src_1.csv", "r") as csvfile:
    f = csv.reader(csvfile)
    first = False  # Skip the header
    for row in f:
        if first == True:
            # Columns C (Mandarin search terms), E (Taiwanese Romanization), and D (Taiwanese Characters) will be used
            csv_data_1.append([row[2], row[4], row[3]])
        else:
            first = True

num = ["2", "3", "5", "7", "8"]  # 1, 4, 6, and 9 are never used
alph = [["a", "e"], ["i", "u"], ["o"]]  # Order of priority to add tone
# In order of 2, 3, 5, 7, 8
vowel_tone = [
    ["á", "à", "â", "ā", "a"],
    ["é", "è", "ê", "ē", "e"],
    ["í", "ì", "î", "ī", "i"],
    ["ú", "ù", "û", "ū", "u"],
    ["ó", "ò", "ô", "ō", "o"],
]

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
                    # Add the rest of the syllable if vowel is not the last letter
                    if len(syll) != len(new_syll):
                        new_syll += syll[syll.index(vowel) + 1 :]
                    corrected = True
            if corrected == False:  # Run the following if the vowel hasn't been corrected yet
                if "o" in syll:  # Next in priority is 'o'
                    # Append first part of syllable up to 'o'
                    new_syll = syll[: syll.index("o")]
                    # Add the 'o' with the corrected tone indication
                    new_syll += vowel_tone[4][tone]
                    if len(syll) != len(new_syll):
                        # Add the rest of the syllable if 'o' is not the last letter
                        new_syll += syll[syll.index("o") + 1 :]
                    corrected = True
            if corrected == False:  # Run the following if the vowel hasn't been corrected yet
                # Look for the last i or u
                for y in range(-1, -len(syll), -1):
                    if syll[y] in alph[1]:
                        new_syll = syll[:y]
                        new_syll += vowel_tone[alph[1].index(syll[y]) + 2][tone]
                        if len(syll) != len(new_syll):
                            new_syll += syll[y + 1 :]
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
with open("src_2.csv", "r") as csvfile:
    f = csv.reader(csvfile)
    first = False
    for row in f:
        if first == True:
            cleanx = ""
            for char in row[3]:
                if ord(char) != 781:
                    cleanx += char
            # Using columns for 華語, 台語, 備存對照, and 台羅
            csv_data_2.append([row[1], row[2], row[4], cleanx])
        else:
            first = True
# Turn into numpy array to slice columns easier
cleaned_2 = np.array(csv_data_2)

# Read and clean source 3
csv_data_3 = []
with open("src_3.csv") as csvfile:
    f = csv.reader(csvfile)
    first = False
    for row in f:
        if first == True:
            csv_data_3.append([row[2], row[3]])  # Using columns for 華語 and 漢字
        else:
            first = True
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
with open("src_4.csv") as csvfile:
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

exceptions_csv = []
with open("exceptions.csv") as csvfile:
    f = csv.reader(csvfile)
    first = False
    for row in f:
        if first == True:
            exceptions_csv.append([])  # Create a new row
            # Separate search terms (Example: ;一定;確定;)
            split = row[2].split(";")
            # Remove extra space
            split.pop(0)
            split.pop(-1)
            exceptions_csv[-1].append(split)  # Final is [一定, 確定]
            # Also include Taiwanese Romanization and Download Link
            exceptions_csv[-1].extend([row[4], row[5]])
        else:
            first = True

src_exc_search = []
src_exc_code = []
src_exc_link = []
for row in exceptions_csv:
    src_exc_search.append(row[0])
    src_exc_code.append(row[1])
    src_exc_link.append(row[2])

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def gfg():
    if request.method == "POST":
        en = request.form.get("en")
        cn = request.form.get("cn")
        color = request.form.get("color")

        mandarin = ""
        if en != None:
            mandarin = GoogleTranslator(source="auto", target="zh-TW").translate(en)
        else:
            mandarin = cn
            en = ""

        conv = []
        conv.append(mandarin)
        cn_trans = conv

        # Now the Mandarin translation of the full sentence needs to be split into
        # individual words that can be found in the Mandarin-Taiwanese database

        # Gate 1: Punctuation
        punc = ["，", "。", "？", "”", "“", "：", " ", "！"]
        for sym in punc:
            for item in cn_trans:
                # Try to split the phrase with the current symbol selected in the punc list
                split = item.split(sym)
                ind = cn_trans.index(item)
                original_length = len(cn_trans)
                cn_trans.pop(ind)  # Remove the phrase pre-split
                # Insert newly splitted segments back into the list
                cn_trans[ind:ind] = split
                if len(cn_trans) > original_length:
                    item = cn_trans[ind + 1]  # Set the next item to be checked

        # Sometimes there may be some values of '' left in the list that need to be removed
        remove_space = []
        for piece in cn_trans:
            if piece != "":
                remove_space.append(piece)
        cn_trans = remove_space

        exceptions = ["吃"]
        for exc in exceptions:
            item_key = 0
            while item_key < len(cn_trans):
                split = cn_trans[item_key].split(exc)
                remove_space = []
                for piece in split:
                    if piece == "":
                        split[split.index(piece)] = exc

                ind = cn_trans.index(cn_trans[item_key])
                original_length = len(cn_trans)
                cn_trans.pop(ind)
                cn_trans[ind:ind] = split
                item_key = ind + 2

        # Gate 2: Remove characters from the end until the remainder
        # matches a search term in source 2, 3, or 4
        for item in cn_trans:
            test_strip = item
            while len(test_strip) > 1:  # Keep running until test_strip is left as a single character
                found = False
                # If test_strip already matches a search term in sources 2, 3, or 4
                if (test_strip in cleaned_2[:, 0]) or (test_strip in cleaned_3_4[:, 0]):
                    found = True
                else:
                    # If not in sources 2, 3, or 4, try source 1
                    found = search_csv_1(test_strip)
                if found == False:
                    # If it still doesn't match a search term, remove the last character and try again
                    test_strip = test_strip[:-1]
                else:  # If it has been found in any of the sources, split the phrase
                    ind = cn_trans.index(item)
                    cn_trans.pop(ind)
                    # Remainder is the back part of the split
                    remainder = item[len(test_strip) :]
                    # Insert the split parts back into the list
                    cn_trans[ind:ind] = [test_strip, remainder]
                    # Set the item to the next after the test_strip
                    item = cn_trans[ind + 1]
                    break  # Break out of the while loop once the test_strip matches a search term
            if len(test_strip) == 1:  # If the test_strip is only 1 character long, it should be by itself
                ind = cn_trans.index(item)
                cn_trans.pop(ind)
                remainder = item[len(test_strip) :]
                cn_trans[ind:ind] = [test_strip, remainder]
                item = cn_trans[ind + 1]
            if item == "":  # Remove if it's just a blank
                cn_trans.pop(cn_trans.index(item))
        print(cn_trans)

        romanized = ""

        key = random.randint(1, 10000)
        count = 0  # Number to name the mp3 file so they are in sentence order when downloaded
        now = str(datetime.now())
        hour = now[11:13]
        file_count = 0
        files = os.listdir("static")
        for file in files:
            if file[-3:] == "mp3":
                if int(file[0:2]) <= int(hour) - 1 or int(file[0:2]) > int(hour):  # Remove files from 1 hour ago
                    os.remove(f"static/{file}")
        for word in cn_trans:
            code = ""
            url = ""

            # First: Look for word in exceptions list
            match = []
            for s_list in src_exc_search:
                for search_term in s_list:
                    if word == search_term:
                        code = src_exc_code[src_exc_search.index(s_list)]
                        romanized += code
                        url = src_exc_link[src_exc_search.index(s_list)]
                        break

            # Second: Look for word in source 2
            if code == "":
                if word in cleaned_2[:, 0]:
                    # Get location of all rows that have search term matching Mandarin exactly
                    selector = np.array([word == s for s in cleaned_2[:, 0].flat]).reshape(cleaned_2[:, 0].shape)
                    match = cleaned_2[selector]  # Select the rows
                    # If Mandarin also matches Taiwanese exactly, set the mp3 download code to the number in column E
                    if word in match[:, 1]:
                        code = list(cleaned_2[:, 2])[list(cleaned_2[:, 1]).index(word)]
                        # print(code)
                        addon = (list(cleaned_2[:, 3])[list(cleaned_2[:, 1]).index(word)]).split("/")
                        # Also concatenate the romanization
                        romanized += addon[0]
                    # If the Mandarin is not just one character, check for matching Taiwanese partially
                    elif len(word) != 1:
                        parts = []
                        for x in range(len(word)):
                            # Separate characters into a list
                            parts.append(word[x])
                        for p in parts:
                            for m in match[:, 1]:
                                if p in m:  # If part of Mandarin characters match Taiwanese, set the mp3 download code to the number in column E
                                    code = list(cleaned_2[:, 2])[list(cleaned_2[:, 1]).index(m)]
                                    addon = (list(cleaned_2[:, 3])[list(cleaned_2[:, 1]).index(m)]).split("/")
                                    romanized += addon[0]
                                    break  # Break out of loop once a matching word has been found
                    if code == "":  # If a matching Taiwanese word still hasn't been found
                        # If none of the Mandarin matches the Taiwanese, just pick the top choice
                        code = match[0][2]
                        addon = (match[0][3]).split("/")
                        romanized += addon[0]
                    # Insert the mp3 download code into the full link for words of source 2
                    add_0 = ""
                    for x in range(5 - len(code)):
                        add_0 += "0"
                    add_0 += code
                    url = f"https://1763c5ee9859e0316ed6-db85b55a6a3fbe33f09b9245992383bd.ssl.cf1.rackcdn.com/{add_0}.mp3"
                    print(url)

            # Third: Look for word in sources 3 and 4
            if code == "":
                if word in cleaned_3_4[:, 0]:
                    selector = np.array([word in s for s in cleaned_3_4[:, 0].flat]).reshape(cleaned_3_4[:, 0].shape)  # Get location of all rows that have search term matching Mandarin exactly
                    match = cleaned_3_4[selector]  # Select the rows
                    # If Mandarin also matches Taiwanese exactly, set the mp3 download code to the romanization in column D
                    code = match[0, 1]  # Set mp3 download code to romanization
                    url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={code}"
                    addon = (match[0, 1]).split("/")
                    romanized += addon[0]  # Concatenate the romanization

            # Fourth: Look for a word in source 1
            if code == "":
                match = []
                for s_list in src_1_search:
                    for search_term in s_list:
                        if word == search_term:
                            # Set the code to the romanization of the matching position
                            match.append(src_1_tai[src_1_search.index(s_list)])
                            # Concatenate the romanization
                if word in match:
                    code = src_1_code[src_1_tai.index(match[match.index(word)])]
                    addon = (src_1_code[src_1_tai.index(match[match.index(word)])]).split("/")
                    romanized += addon[0]
                elif len(match) > 0:
                    code = src_1_code[src_1_tai.index(match[0])]
                    addon = (src_1_code[src_1_tai.index(match[0])]).split("/")
                    romanized += addon[0]
                if code != "":  # If a match was found in source 1, insert the romanization into the full link for downloading words of source 1
                    url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={code}"

            # Fifth: Use Mandarin TTS from Google Translate
            if code == "":
                full_split = []
                for char in word:
                    # Separate the Mandarin into individual characters in a list
                    full_split.append(char)
                # Join together with'%20' between each character
                code = "%20".join(full_split)
                # Get the link to the Google Translate audio
                url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={code}.&tl=zh-TW&total=1&idx=0&textlen=15&tk=350535.255567&client=webapp&prev=input"
                # Go to the site itself to get the romanization
                romanized += pinyin.get(word)

            # Download the mp3 to the Output folder
            myfile = requests.get(url)
            open(f"static/{hour}_{key}_{count}.mp3", "wb").write(myfile.content)
            b = os.path.getsize(f"static/{hour}_{key}_{count}.mp3")
            if b < 1000:  # If download failed, try different link
                url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={addon[0]}"
                myfile = requests.get(url)
                open(f"static/{hour}_{key}_{count}.mp3", "wb").write(myfile.content)
            count += 1  # Increment the count number to prepare for the next audio file
            romanized += " "  # Add a space between each word
            file_count += 1
        print(romanized)

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
        )
    return render_template("index.html")


app.run(host="0.0.0.0", port=81)
