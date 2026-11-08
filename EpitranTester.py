import jiwer
import pandas as pd
import epitran
predictions = []
references = []

epi = epitran.Epitran('est-Latn') #Epitran module (pre + map + post) to use
df = pd.read_csv("krl-final.csv") #file to read from
word_list = df["word"].to_list()
correct_list = df["transcription"].to_list()

for j in range(len(word_list)):
    word = word_list[j]
    correct = correct_list[j]
    output = epi.transliterate(word)

#calculate PER and print incorrect output
    if output != correct:
        print(output, correct)

    predictions.append(output)
    references.append(correct)

wer = jiwer.wer(references, predictions)
cer = jiwer.cer(references, predictions)

print(f"Word Error Rate (WER): {wer * 100:.2f}%")
print(f"Character Error Rate (CER): {cer * 100:.2f}%")

