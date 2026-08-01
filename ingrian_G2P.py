import csv
import pandas as pd
from jiwer import wer

error_list = []
new_list= []
new_reference=[]

def right(word, index):
    if index + 1 < len(word):
        return word[index + 1]
    return ""


def left(word, index):
    if index - 1 >= 0:
        return word[index - 1]
    return ""

# Opens CSV file, filters and reads each line and adds orthography to wordlist and IPA to reference
df=pd.read_csv("ingrian_normal.csv")
orthography_list=df["orthography"].to_list()
reference=df["ipa"].to_list()

# 1 to 1 or 2 G2P
g2pdict = {
        "š": "ʃ",
        "ž": "ʒ",
        "c": "t͡ʃ",
        "v": "ʋ",
        "a": "ɑ",
        "ä": "æ",
        "ö": "ø",
        "ь":"ɨ",
        "g":"ɡ"
        }

vowels = ('a', 'e', 'o', 'i', 'u', 'ä', 'ö','ь','y')

word_count = 0

errors = 0

for w in range(len(orthography_list)):
    word=((orthography_list[w]).lower())
    char_index = 0

    output = ""

    for c in range(len(word)):
        char=word[c]

        # WORD FINAL SECTION

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

            # Word Final l (Not accurate)

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
                elif left(word, c - 1) == 'ä' or left(word, c - 1) == 'e' or left(word,c - 1) == 'y':
                    output += 'lːæ'
                else:
                    output += 'l'

            # Word Final ks => kse

        elif char == 's' and left(word, c) == 'k' and c == len(word) - 1:
            output += "se"

            # Word Final mp => mpi

        elif char == 'p' and left(word, c) == 'm' and c == len(word) - 1:
            output += "pi"

        # MORPHOLOGY SECTION

            # An attempt at fixing the -in vs -ine morphological pattern by putting in a common morphological pattern

        elif c == (len(word) - 1) and char == 'n' and left(word, c) == 'i' and left(word,c - 1) in ['ä', 'a', 'o', 'i']:
            if left(word, c - 1) in ["ö", 'o'] and left(word, c - 2) == "t":
                output += 'n'
            elif left(word, c - 1) == 'i':
                output = output.removesuffix('ː')
                output += 'ne'
            else:
                output += "ne"

        #OTHER

            #Nasal Assimilation
        elif char == "n" and (right(word, c) == 'k' or right(word, c) == 'g'):
            output += "ŋ"

            # ts => t͡s
        elif char == 's' and left(word, c) == 't':
            output = output.removesuffix('t')
            output += "t͡s"

            # Gemination/Long Vowels
        elif left(word, c) == char:
            #Handling a common non-gemination case
            if char in ['p','r','s','l'] and right(word,c) == 'i' and right(word,c+1) in ['a','ä'] and c+2 ==len(word)-1:
                pass
            elif char in g2pdict:
                output = output.removesuffix(g2pdict[char])
                output += (g2pdict[char] + 'ː')
            else:
                output = output.removesuffix(char)
                output += (char + 'ː')

            # 'j' epenthesis (Not Accurate)
        elif char in 'i' and right(word, c) in vowels and right(word, (c + 1)) in vowels:
            if char in g2pdict:
                output += g2pdict[char] + 'j'
            else:
                output += char + 'j'

            # h after r and n is lost
        elif char == 'h' and left(word,c) in ['r','n']:
            pass

            # non-syllabic vowels
        elif char in ["i","u","y"] and left(word, c) in vowels:
            if left(word, c - 1) == left(word, c):
                output += char
            else:
                output += char + "̯"

            # 1 to 1
        elif char in g2pdict:
            output += g2pdict[char]

            # no changes
        else:
            output += char

            # index
        c += 1


    #creation of list
    new_list.append("/ˈ{}/".format(output))

    print("{}=>/ˈ{}/".format(word, output))

    #calculation of error
    error = wer(reference[w], new_list[w])

    # creation of errorlist
    if error == 1:
        errors+=1
        error_word=(orthography_list[w],reference[w], new_list[w])
        error_list.append(error_word)

    word_count=w

# errorlist printed
for error_word in error_list:
    print(error_word)

# errorlist csv
with open('ingrian_errors.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(error_list)

#Error rate
print('Error Percentage is:',str(((errors/word_count)*100))+'%')
print('Accuracy is:',str(100-(int((errors/word_count)*100)))+'%')