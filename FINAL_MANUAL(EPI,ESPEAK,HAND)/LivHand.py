import jiwer
import pandas as pd
predictions = []
references = []

g2p_dict = {'ž': 'ʒ', 'š': 'ʃ', 'ļ': 'ʎ', 'ņ': 'ɲ', 'ț': 'c', 'ḑ': 'ɟ', 'ŗ': 'rʲ', 'ē': 'eː', 'ī': 'iː', 'ō': 'oː',
            'ū': 'uː', 'y': 'y', 'ü': 'y', 'ä': 'æ', 'õ': 'ə', 'ǭ': 'ɒː', 'ȭ': 'əː', 'ǟ': 'æː', 'ȯ': 'ɤ', 'ȱ': 'ɤː',
            'a': 'ɑ', 'ā': 'ɑː', 'g': 'ɡ', 'ɡ':'ɡ'}
consonant_list = ['v', 'b', 'd', 'g', 'ɡ', 'f', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'z', 'ž', 'š', 'ļ', 'ņ',
                  'ț', 'ḑ', 'ŗ']
vowel_list = ['a', 'e', 'i', 'o', 'u', 'ā', 'ē', 'ī', 'ō', 'ū', 'y', 'ü', 'ä', 'õ', 'ǭ', 'ȭ', 'ǟ', 'ȯ', 'ȱ']
df = pd.read_csv("liv-final.csv")
words_list = df["word"].to_list()
correct_list = df["transcription"].to_list()

for j in range(len(words_list)):
    word = words_list[j]
    correct = correct_list[j]

    word = word.lower()
    output = ""

    for i in range(len(word)):
        if word[i] in vowel_list: #vowels transliterate normally
            if word[i] in g2p_dict:
                output += g2p_dict[word[i]]
            else:
                output += word[i]
        elif word[i] in consonant_list:
            if i > 0 and word[i - 1] == word[i]: #handle geminate consonants
                prev_ipa = g2p_dict.get(word[i - 1], word[i - 1])
                output = output[:-len(prev_ipa)]
                output += prev_ipa + 'ː'
            elif word[i] in g2p_dict: #normal consonants
                output += g2p_dict[word[i]]
            else:
                output += word[i]
        elif word[i] == '’': #glottalization symbol
            output += 'ˀ'

    #postprocessing
    output = output.replace('tʃ', 't͡ʃ') #formatting
    output = "ˈ" + output #primary stress addition
    output = output.replace("ˈə","ˈɯ") #stress-syllable vowel-shifts
    if len(output) >= 3 and output[1] in consonant_list and output[0] == "ˈ" and output[2] == "ə":
        output = output.replace("ə","ɯ", 1)
    if len(output) < 3 and output[0] == "ə":
        output = output.replace("ə", "ɯ", 1)

#calculate PER and print incorrect output
    if output != correct:
        print(output, correct)

    predictions.append(output)
    references.append(correct)

wer = jiwer.wer(references, predictions)
cer = jiwer.cer(references, predictions)

print(f"Word Error Rate (WER): {wer * 100:.2f}%")
print(f"Character Error Rate (CER): {cer * 100:.2f}%")

