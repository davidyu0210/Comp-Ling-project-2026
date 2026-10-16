consonants = ["p", "b", "t", "d", "k", "ɡ", "t͡ʃ", "d͡ʒ", "s", "z", "ʃ", "ʒ", "h", "f", "v", "m", "n", "ŋ", "l", "r", "j"]
vowels = ["i", "y", "u", "e", "ø", "o", "æ", "ɑ"]

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def mappings(word):
    mappings = {"ä": "æ", "ö": "ø", "š": "ʃ", "č": "t͡ʃ", "ž": "ʒ", "v": "ʋ", "ʹ": "ʲ", "a": "ɑ", "g": "ɡ"}
    word = list(word)
    for i, char in enumerate(word):
        if char in mappings.keys():
            word[i] = mappings[char]
    word = ''.join(word)
    return word

def palatilization(word): #coronals in front of front vowels get palatilized
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
        if word[i] == "n" and word[i+1] == "ɡ":
            word[i] = "ŋ"
    word = ''.join(word)
    return word

def edit_distance(str1: str, str2: str) -> int:
    """Levenshtein (character) edit distance between two IPA strings, after
    stripping any wrapping /.../ slashes from both."""
    str1 = str1.strip("/")
    str2 = str2.strip("/")
    m, n = len(str1), len(str2)

    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],
                    dp[i][j - 1],
                    dp[i - 1][j - 1]
                )

    return dp[m][n]

def g2p(word):
    word = apply_stress(word)
    word = gemination(word)
    word = mappings(word)
    word = palatilization(word)
    word = desyllabification(word)
    word = velarization(word)
    return(f"/{word}/")

def parse_args():
    import argparse
    ap = argparse.ArgumentParser(description="Run the rule-based G2P over an orthography,/ipa/ CSV "
                                             "and report PER and WER.")
    ap.add_argument("-i", "--input", type=Path, default=ROOT / 'data' / 'karelian_terms.csv',
                    help="input CSV (default: data/karelian_terms.csv)")
    ap.add_argument("-o", "--output", type=Path, default=None,
                    help="output CSV (default: outputs/karelian_output.csv for karelian_terms.csv, "
                         "else outputs/<input stem>_output.csv)")
    ap.add_argument("--no-secondary-stress", action="store_true",
                    help="remove secondary stress marks (ˌ) from gold and predicted IPA "
                         "before scoring (data files are not modified)")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    output_path = args.output
    if output_path is None:
        stem = "karelian" if args.input.stem == "karelian_terms" else args.input.stem
        suffix = "_no_secondary_stress" if args.no_secondary_stress else ""
        output_path = ROOT / 'outputs' / f'{stem}{suffix}_output.csv'

    # Same loading and scoring as the neural pipeline (g2p_model.load_pairs /
    # evaluate_detailed): orthography lowercased, slashes stripped, exact
    # (orthography, IPA) duplicates dropped, and PER = total edits / total gold
    # length, so the rule-based and neural PERs are directly comparable.
    pairs = []
    seen = set()
    with open(args.input, newline='', encoding='utf-8-sig') as csvfile:
        for i, row in enumerate(csv.reader(csvfile)):
            if len(row) < 2:
                continue
            word = row[0].strip().lower()
            gold = row[1].strip().strip("/")
            if i == 0 and word == "orthography":
                continue  # header row (e.g. karelian_raw.csv)
            if args.no_secondary_stress:
                gold = gold.replace("ˌ", "")
            if not word or not gold or (word, gold) in seen:
                continue
            seen.add((word, gold))
            pairs.append((word, gold))

    results = []
    total_edits, total_len, word_errors = 0, 0, 0
    for word, gold in pairs:
        pred = g2p(word).strip("/")
        if args.no_secondary_stress:
            pred = pred.replace("ˌ", "")
        edits = edit_distance(pred, gold)
        total_edits += edits
        total_len += len(gold)
        word_errors += int(pred != gold)
        results.append((edits / len(gold), word, gold, pred))

    per = total_edits / total_len
    wer = word_errors / len(pairs)  # share of words not exactly matching gold

    results.sort()
    for r in results:
        print(r)

    print(f"input: {args.input}  words: {len(pairs)}"
          + ("  (secondary stress removed)" if args.no_secondary_stress else ""))
    print(f"PER: {per*100:.2f}% ({total_edits} edits / {total_len} gold phones)")
    print(f"WER: {wer*100:.2f}% ({word_errors}/{len(pairs)} words wrong)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(["orthography", "gold", "prediction", "per"])
        for word_per, word, gold, pred in results:
            spamwriter.writerow([word, f"/{gold}/", f"/{pred}/", round(word_per, 2)])
    print(f"saved {output_path}")
