import pandas as pd
from jiwer import cer
from phonemizer import phonemize

wer_error_list = []
languages_list = ['fi','et','hu','smj']
files = ['krl-final','liv-final','izh-final']

for file in files:

    #Reads file and makes a list for orthography and IPA
    df=pd.read_csv(file+'.csv')
    orthography_list=df["word"].to_list()
    reference=df["transcription"].to_list()

    print('\n'+file+'\n')

    # Goes through every word in the orthography list
    for language in languages_list:

        wer_errors = 0
        word_count = 0
        cer_error_sum = 0
        for w in range(len(orthography_list)):

            #Minor Capitalization normalization
            word=((orthography_list[w]).lower())

            word=word.replace('ɡ','g').replace('ḑ','d').replace('ь','i').replace("ʹ","'")

            #Phonemizer
            output=phonemize(word, language=language)

            output="ˈ{}".format(output)

            output=output.replace(" ","").replace('a','ɑ')

            #Error calculation
            cer_error = cer(reference[w], output)

            cer_error_sum += cer_error

            word_count = len(orthography_list)

        #Total Error Rate calculation

        print(language)
        print('Cer average error rate is:',str(((cer_error_sum/word_count)*100))+'%')
