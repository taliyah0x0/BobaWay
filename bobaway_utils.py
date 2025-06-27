import csv
import numpy as np
from constants import num, alph, vowel_tone, consonants


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
