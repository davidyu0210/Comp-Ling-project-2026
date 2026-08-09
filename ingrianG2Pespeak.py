import pandas as pd
from jiwer import wer
from jiwer import cer
from phonemizer import phonemize

wer_error_list = []
wer_errors = 0
word_count = 0
cer_error_sum = 0


#Reads file and makes a list for orthography and IPA
df=pd.read_csv('ingrian_alldata.csv')
orthography_list=df["orthography"].to_list()
reference=df["ipa"].to_list()

# Goes through every word in the orthography list
for w in range(len(orthography_list)):
    #Minor Capitalization normalization
    word=((orthography_list[w]).lower())

    #Phonemizer
    output=phonemize(word, language='fi')

    #Some formatting and minor normalization
    output="/ˈ{}/".format(output)

    output=output.replace(" ","").replace('a','ɑ')

    #Error calculation
    wer_error = wer(reference[w], output)
    cer_error = cer(reference[w], output)
    print(cer_error)
    print(wer_error)

    cer_error_sum += cer_error

    if wer_error == 1:
        wer_errors+=1
        wer_error_word = (orthography_list[w], reference[w], output)
        wer_error_list.append(wer_error_word)

    word_count=w

    #Printing out every word
    print('Word={}\nPredicted={}\nIPA={}\n'.format(word,output,reference[w]))

#Printing every WER error
for wer_error_word in wer_error_list:
    print(wer_error_word)

#Total Error Rate calculation
print('Wer error rate is:',str(((wer_errors/word_count)*100))+'%')
print('Cer average error rate is:',str(((cer_error_sum/word_count)*100))+'%')