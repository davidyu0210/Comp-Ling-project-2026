import jiwer
import pandas as pd
import epitran
predictions = []
references = []

# Initialize Epitran (replace 'xxx-Latn' with your language code)
epi = epitran.Epitran('kar-Latn')

skip_count = 0
df = pd.read_csv("kar-norm.csv")
words_list = df["word"].to_list()
correct_list = df["transcription"].to_list()

for j in range(len(words_list)):
    word = words_list[j]
    correct = correct_list[j]
    if type(word) != str or type(correct) != str:
        print(word, correct)
        skip_count += 1
        continue

    # Use Epitran to transcribe the word
    output = epi.transliterate(word)
    
    # ONLY FOR INGRIAN AND KARELIAN (I made a mistake and this is the easiest way to fix it)
    output = "/" + output + "/"
    
    # print all errors
    if output != correct:
        print(output, correct)

    predictions.append(output)
    references.append(correct)

wer = jiwer.wer(references, predictions)
cer = jiwer.cer(references, predictions)

print(f"Word Error Rate (WER): {wer * 100:.2f}%")
print(f"Character Error Rate (CER): {cer * 100:.2f}%")

