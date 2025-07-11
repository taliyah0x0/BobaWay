from constants import consonants, vowels, num, match_lett
from bobaway_utils import add_tones
import os
import requests
from pydub import AudioSegment

def get_endings(og, ogg, change, filename, page, prev, last):
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
    return endings, {
        "og": og,
        "ogg": ogg,
        "change": change,
        "filename": filename,
        "page": page,
        "prev": prev,
        "last": last
    }