import re

# Returns true if the given string is a hanzi character. Otherwise, false. 
def checkHanzi(hanzi):
    return re.search(u'[\u4e00-\u9fff]', hanzi)

# Returns true if the given string consists entirely of Latin alphabet. Otherwise, false. 
def checkRoman(roman):
    char_set = "abcdefghijklmnopqrstuvwxyz"
    return all((True if x in char_set else False for x in roman))

# Returns true if the entry has already been added. 
def checkEntryExistence(db, language, h, r):
    found = False 
    search = db.get_entry_by_hanzi_and_roman(language, h, r)
    if search:
        found = True
    return found 