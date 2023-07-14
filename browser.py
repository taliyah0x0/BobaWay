# The biggest flaw of BobaWay is the inaccuracies in translation,
# so I wrote this script that uses an existing Mandarin to Taiwanese translator
# that provides much better natural-sounding translations and audio

# To use, you'll have to download this file and run with Python in Terminal or Console

# Include libraries
import asyncio
from pyppeteer import launch
from deep_translator import GoogleTranslator

# Get user input
phrase = input("Please enter a phrase in English: ")

async def to_tw():  # Function for English to Taiwanese translation

    browser = await launch({'headless': False})
    page = await browser.newPage()

    # Translate English to Taiwanese
    cn_trans = GoogleTranslator(source="auto", target="zh-TW").translate(phrase)

    # Using this Mandarin to Taiwanese translator
    await page.goto("http://tts001.iptcloud.net:8804/")

    # Type in the translated Mandarin phrase
    cn_input = ".reference-input"
    await page.waitForSelector(cn_input)
    await page.type(cn_input, cn_trans)
    await page.waitFor(len(cn_trans) * 50)

    # Click on the button to get romanization
    bt = "#js-translate"
    await page.waitForSelector(bt)
    await page.click(bt)
    await page.waitFor(len(cn_trans) * 50)

    # Get the romanization and print in console
    selector = await page.querySelectorAll('#text1')
    valueSelector = await selector[0].getProperty("value")
    romanized = await valueSelector.jsonValue()

    print(romanized)

    # Click on the button to get audio
    bt2 = "#button1"
    await page.waitForSelector(bt2)
    await page.click(bt2)
    await page.waitFor(len(cn_trans) * 200)

    # Download the audio file
    await page.waitForSelector("#audio1", {'hidden': False})

    audio = await page.J('[id=audio1]')
    audio_url = await page.evaluate('(audio_element) => audio_element.getAttribute("src")', audio)

    await page.evaluate('''() => {document.body.innerHTML += '<a id="download_link" href="#" download="">Download</a>';}''')

    await page.evaluate('''([audio_url, phrase]) => {
        let dom = document.querySelector('#download_link');
        dom.href = audio_url;
        dom.download = phrase;
    }''', [audio_url, phrase])

    await page.click('#download_link')

    await page.waitFor(len(cn_trans) * 500)

asyncio.get_event_loop().run_until_complete(to_tw())
