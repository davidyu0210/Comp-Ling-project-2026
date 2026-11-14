import pandas as pd
import jiwer

consonants = ["p", "b", "t", "d", "k", "ɡ", "t͡ʃ", "d͡ʒ", "s", "z", "ʃ", "ʒ", "h", "f", "v", "m", "n", "ŋ", "l", "r", "j"]
vowels = ["i", "y", "u", "e", "ø", "o", "æ", "ɑ"]

def mappings(word):
    mappings = {"ä": "æ", "ö": "ø", "š": "ʃ", "č": "t͡ʃ", "ž": "ʒ", "v": "ʋ", "ʹ": "ʲ", "a": "ɑ", "g": "ɡ"}
    word = list(word)
    for i, char in enumerate(word):
        if char in mappings.keys():
            word[i] = mappings[char]
    word = ''.join(word)
    return word

def palatalization(word): #coronals in front of front vowels get palatalized
    palatalizable = ["t", "d", "s", "z", "l", "n"]
    front_vowels = ["i", "y", "e", "ø", "æ"]
    output = []
    for i, char in enumerate(word):
        output.append(char)
        if char in palatalizable:
            j = i + 1
            if j < len(word) and word[j] == "ː": #geminates palatalize too: tː + i -> tʲː
                j += 1
            if j < len(word) and word[j] in front_vowels:
                output.append("ʲ")
    word = ''.join(output)
    for c in palatalizable: #orthographic palatal geminates: tʹtʹ -> tʲtʲ -> tʲː
        word = word.replace(c + "ʲ" + c + "ʲ", c + "ʲː")
    return word

def gemination(word):
    word = list(word)
    for i in range(len(word)-1):
        if word[i] == word[i+1]:
            word[i+1] = "ː"
    word = ''.join(word)
    return word

def desyllabification(word): #second vowels in diphthongs get desyllabified
    desyllabified = {"i": "i̯", "y": "y̯", "u": "u̯", "e": "e̯", "ø": "ø̯", "o": "o̯", "æ": "æ̯", "ɑ": "ɑ̯"}
    word = list(word)
    for i in range(len(word)-1):
        if word[i] in vowels and word[i+1] in vowels:
            word[i+1] = desyllabified[word[i+1]]
    word = ''.join(word)
    return word

def apply_stress(word):
    word = list(word)
    word.insert(0, "ˈ")
    word = "".join(word)
    return word

def velarization(word):
    word = list(word)
    for i in range(len(word)-1):
        if word[i] == "n" and (word[i+1] == "ɡ" or word[i+1] == "k"):
            word[i] = "ŋ"
    word = ''.join(word)
    return word

def g2p(word):
    word = apply_stress(word)
    word = gemination(word)
    word = mappings(word)
    word = palatalization(word)
    word = desyllabification(word)
    word = velarization(word)
    return word

predictions = []
references = []

df = pd.read_csv("krl-final.csv") #file to read from
word_list = df["word"].to_list()
correct_list = df["transcription"].to_list()

for j in range(len(word_list)):
    word = str(word_list[j]).lower()
    correct = correct_list[j]
    output = g2p(word)

#calculate PER and print incorrect output
    if output != correct:
        print(output, correct)

    predictions.append(output)
    references.append(correct)

cer = jiwer.cer(references, predictions)

print()
print('Overall Phoneme Error Rate (CER):', str(round(cer * 100, 2)) + '%')
