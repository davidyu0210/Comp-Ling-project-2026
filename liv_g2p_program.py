import jiwer
import pandas as pd

g2p_dict = {'ž': 'ʒ', 'š': 'ʃ', 'ļ': 'ʎ', 'ņ': 'ɲ', 'ț': 'c', 'ḑ': 'ɟ', 'ŗ': 'rʲ', 'ē': 'eː', 'ī': 'iː', 'ō': 'oː',
            'ū': 'uː', 'y': 'y', 'ü': 'y', 'ä': 'æ', 'õ': 'ə', 'ǭ': 'ɒː', 'ȭ': 'əː', 'ǟ': 'æː', 'ȯ': 'ɤ', 'ȱ': 'ɤː',
            'a': 'ɑ', 'ā': 'ɑː', 'g': 'ɡ'}
consonant_list = ['v', 'b', 'd', 'g', 'f', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'r', 's', 't', 'z', 'ž', 'š', 'ļ', 'ņ',
                  'ț', 'ḑ', 'ŗ']
vowel_list = ['a', 'e', 'i', 'o', 'u', 'ā', 'ē', 'ī', 'ō', 'ū', 'y', 'ü', 'ä', 'õ', 'ǭ', 'ȭ', 'ǟ', 'ȯ', 'ȱ']
skip_count = 0
df = pd.read_csv("liv_data.csv")
words_list = df["word"].to_list()
correct_count = 0
correct_list = df["transcription"].to_list()

for j in range(len(words_list)):
    word = words_list[j]
    correct = correct_list[j]
    if type(word) != str or type(correct) != str:
        print(word, correct)
        skip_count += 1
        continue

    word = word.lower()  # Convert to lowercase
    output = ""

    for i in range(len(word)):
        # Handle vowels
        if word[i] in vowel_list:
            if word[i] in g2p_dict:
                output += g2p_dict[word[i]]
            else:
                output += word[i]

        # Handle consonants
        elif word[i] in consonant_list:
            if i > 0 and word[i - 1] == word[i]:
                prev_ipa = g2p_dict.get(word[i - 1], word[i - 1])
                output = output[:-len(prev_ipa)]  # Remove the previous consonant
                output += prev_ipa + 'ː'
            elif word[i] in g2p_dict:
                output += g2p_dict[word[i]]
            else:
                output += word[i]

        # Handle apostrophe
        elif word[i] == '’':
            output += 'ˀ'

    # Apply replacements after the entire word is processed
    output = output.replace('tʃ', 't͡ʃ')
    if 'ō' in word and 'gõ' in word:
        output = output.replace('oː','ɒː')
    if output == 'jo':
        output = 'juo'
    output = "/" + output + "/"
    if output == correct:
        correct_count += 1
    else:
        print(output, correct)

print(100 * correct_count / (len(words_list) - skip_count))
