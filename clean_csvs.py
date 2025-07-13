import csv
import numpy as np
from constants import num, alph, vowel_tone

def clean_csv_1():
  '''
    Clean source 1.
    Returns:
      A list of cleaned data from source 1.
  '''
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
  return cleaned_1


# Function for checking if the mandarin translation exists as a search term in source 1
def search_csv_1(text, src_1_search):
  '''
    Check if the mandarin translation exists as a search term in source 1.
    Args:
      text: The mandarin translation to check
    Returns:
      True if the mandarin translation exists as a search term in source 1, False otherwise
  '''
  for s_list in src_1_search:
    for search_term in s_list:
      if text == search_term:
        return True
  return False


def clean_csv_2():
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
  cleaned_2 = np.array(csv_data_2, dtype=object)
  return cleaned_2


def clean_csv_3():
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
  return cleaned_3


def clean_csv_4():
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
  return cleaned_4


def clean_3_4_combined():
  cleaned_3 = clean_csv_3()
  cleaned_4 = clean_csv_4()
  cleaned_3_4 = cleaned_3 + cleaned_4
  cleaned_3_4 = np.array(cleaned_3_4, dtype=object)
  return cleaned_3_4