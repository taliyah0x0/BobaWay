import os
from datetime import datetime
import requests
from pydub import AudioSegment
import numpy as np
from deep_translator import GoogleTranslator

def remove_recent_files():
    now = str(datetime.now())
    hour = now[11:13]
    files = os.listdir("static/sounds")
    for file in files:
        if file[-3:] == "wav":
            if int(file[0:2]) <= int(hour) - 1 or int(
                file[0:2]) > int(hour):  # Remove files from 1 hour ago
                os.remove(f"static/sounds/{file}")


def get_options_tai(red, cleaned_2, cleaned_3_4, src_1_search, src_1_code, src_1_tai):
    mandarin = GoogleTranslator(source="auto", target="zh-TW").translate(red)

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

    return sorted_options, sorted_tai


def export_audio(sorted_options, hour):
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