import os, re, argparse
import numpy as np
from string import punctuation

def read_file(path, vocab):
    """Read in a single Eng-CHILDES file and update the vocabulary with the words in that file"""
    file = open(path)
    for line in file.readlines():
        # This means that it's the start of a new utterance
        if line[:4] == "%mor":
            for word in [w for w in re.split(r'[ _]', line.strip())[1:]]:
                word = re.split(r'[&-]',word.split("|")[-1])
                if "PAST" in word:
                    word = word[0]
                    if word not in vocab:
                        vocab[word] = 0
                    vocab[word] += 1
    file.close()

def load_unimorph(path):
    """Load in the UniMorph annotations"""
    vocab = {}
    file = open(path)
    for lemma, inflected, feats in [l.strip().split("\t") for l in file.readlines()]:
        if feats == "V;PST":
            vocab[lemma] = inflected
    file.close()
    return vocab

def main(childes_path, unimorph_path, out_path):
    """The main function to extract the data"""
    np.random.seed(42)

    # Get all the .cha filepaths from English-CHILDES
    file_paths = []
    for root, dirs, files in os.walk(childes_path):
        for fname in files:
            if fname.endswith(".cha"):
                file_paths.append(os.path.join(root, fname))

    # Extract the vocabulary
    print(f"Extracting vocabulary from {len(file_paths)} files...")
    vocab = {}
    for f in file_paths:
        read_file(f, vocab)

    # Filter to just past tense verbs
    print(f"Extracted {len(vocab)} words. Filtering through UniMorph...")
    unimorph = load_unimorph(unimorph_path)
    past_tense = {}
    for k, v in sorted(vocab.items(), key=lambda x: x[1], reverse=True):
        if k in unimorph:
            ing = k[-3:] == "ing"
            ing_ang = ing and unimorph[k][-3:] in ["ang"]
            past_tense[k] = (unimorph[k], ing, ing_ang, v)

    print(f"Extracted {len(past_tense)} past tense words.")
    with open(out_path, "w") as f:
        for k, v in sorted(past_tense.items(), key=lambda x: x[1][-1], reverse=True):
            f.write(f"{k}\t{v[0]}\t{v[1]}\t{v[2]}\t{v[3]}\n")
    f.close()



if __name__ == "__main__":
    main("Eng-CHILDES", "eng-unimorph.txt", "eng-past.txt")
    parser = argparse.ArgumentParser()
    parser.add_argument("--childes", required=True, help="Path to German-CHILDES data")
    parser.add_argument("--celex", required=True, help="Path to CELEX data")
    parser.add_argument("--out", required=True, help = "Path to write output data to")
    args = parser.parse_args()
    main(args.childes, args.celex, args.out)