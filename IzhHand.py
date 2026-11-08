import pandas as pd
from jiwer import cer

#methods to take the letters adjacent to a given letter
def right(word, index):
    if index + 1 < len(word):
        return word[index + 1]
    return ""

def left(word, index):
    if index - 1 >= 0:
        return word[index - 1]
    return ""

# choose CSV file and sort into two lists
df = pd.read_csv("izh-final.csv")
orthography_list = df["word"].to_list()
reference = df["transcription"].to_list()

# 1:1 mappings
g2pdict = {"š": "ʃ","ž": "ʒ","c": "t͡ʃ","v": "ʋ","a": "ɑ","ä": "æ","ö": "ø","ь": "ɨ","g": "ɡ"}
vowels = ('a', 'e', 'o', 'i', 'u', 'ä', 'ö', 'ь', 'y')

new_list = []

for w in range(len(orthography_list)):
    word = ((orthography_list[w]).lower())

    output = ""

    for c in range(len(word)):
        char = word[c]

        # Word final st and lt
        if char == 't' and left(word, c) in ['l', 's'] and c == len(word) - 1:
            if left(word, c - 1) in ['a', 'o']:
                output += 'tɑ'
            elif left(word, c - 1) in ['e', 'i'] and left(word, c - 2) == 'o':
                output += 'tɑ'
            elif left(word, c - 1) in ['ä', 'e']:
                output += 'tæ'
            elif left(word, c - 1) == 'i' and left(word, c - 2) == 'e':
                output += 'tæ'
            elif left(word, c - 1) == 'u' and left(word, c - 2) == 'i':
                output += 'tæ'

        # Word Final l
        elif char == 'l' and c == (len(word) - 1):
            if 'lː' in output:
                output = output.replace('lː', 'l')
                if word[c - 1] == 'e':
                    output += 'lːæ'
                elif word[c - 1] in g2pdict:
                    output += 'lː' + g2pdict[word[c - 1]]
                else:
                    output += 'lː' + word[c - 1]
            else:
                output.removesuffix('ː')
                if left(word, c - 1) == 'a':
                    output += 'lːɑ'
                elif left(word, c - 1) == 'i':
                    output += 'lːe'
                elif left(word, c - 1) == 'ä' or left(word, c - 1) == 'e' or left(word, c - 1) == 'y':
                    output += 'lːæ'
                else:
                    output += 'l'

        # Word Final ks => kse
        elif char == 's' and left(word, c) == 'k' and c == len(word) - 1:
            output += "se"

        # Word Final mp => mpi
        elif char == 'p' and left(word, c) == 'm' and c == len(word) - 1:
            output += "pi"

        #-in vs -ine morphological pattern
        elif c == (len(word) - 1) and char == 'n' and left(word, c) == 'i' and left(word, c - 1) in ['ä', 'a', 'o', 'i']:
            if left(word, c - 1) in ["ö", 'o'] and left(word, c - 2) == "t":
                output += 'n'
            elif left(word, c - 1) == 'i':
                output = output.removesuffix('ː')
                output += 'ne'
            else:
                output += "ne"

        #nasal assimilation
        elif char == "n" and (right(word, c) == 'k' or right(word, c) == 'g'):
            output += "ŋ"

        #formatting
        elif char == 's' and left(word, c) == 't':
            output = output.removesuffix('t')
            output += "t͡s"

        #gemination/long vowels
        elif left(word, c) == char:
            if char in ['p', 'r', 's', 'l'] and right(word, c) == 'i' and right(word, c + 1) in ['a', 'ä'] and c + 2 == len(word) - 1:
                pass
            elif char in g2pdict:
                output = output.removesuffix(g2pdict[char])
                output += (g2pdict[char] + 'ː')
            else:
                output = output.removesuffix(char)
                output += (char + 'ː')

        # 'j' epenthesis
        elif char in 'i' and right(word, c) in vowels and right(word, (c + 1)) in vowels:
            if char in g2pdict:
                output += g2pdict[char] + 'j'
            else:
                output += char + 'j'

        # h after r and n is lost
        elif char == 'h' and left(word, c) in ['r', 'n']:
            pass

        # non-syllabic vowels
        elif char in ["i", "u", "y"] and left(word, c) in vowels:
            if left(word, c - 1) == left(word, c):
                output += char
            else:
                output += char + "̯"

        #1:1 mapping
        elif char in g2pdict:
            output += g2pdict[char]

        else:
            output += char

    new_list.append("ˈ{}".format(output))

    if reference[w] != new_list[w]:
        print(reference[w], new_list[w])

overall_cer = cer(reference, new_list)
print()
print(str(round(overall_cer * 100, 2)) + '% PER')