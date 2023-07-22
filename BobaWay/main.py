from flask import Flask, request, render_template
from deep_translator import GoogleTranslator
import requests
import os
import random
from datetime import datetime
import pyppeteer
from pydub import AudioSegment

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
async def gfg():
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

        browser = await pyppeteer.launcher.connect(browserWSEndpoint='wss://chrome.browserless.io?token='+'e4057a02-a262-4d88-9b37-c958c579719c')
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

        # Get the romanization and print in console
        selector = await page.querySelectorAll('#text1')
        valueSelector = await selector[0].getProperty("value")
        romanized = await valueSelector.jsonValue()

        cleaned = ''
        for letter in romanized:
            if letter != '1' and letter != '4' and letter != '6' and letter != '9':
                cleaned += letter

        split_up = cleaned.split(' ')
        print(split_up)

        key = random.randint(1, 10000)
        now = str(datetime.now())
        hour = now[11:13]
        files = os.listdir("static")
        for file in files:
            if file[-3:] == "mp3":
                if int(file[0:2]) <= int(hour) - 1 or int(file[0:2]) > int(hour):  # Remove files from 1 hour ago
                    os.remove(f"static/{file}")

        file_count = 0
        for count in range(len(split_up)):
            url = f"https://hts.ithuan.tw/文本直接合成?查詢腔口=台語&查詢語句={split_up[count]}"
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
