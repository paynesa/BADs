import os, re, argparse
import numpy as np
from string import punctuation

def read_file(path, vocab):
    """Read in a single German-CHILDES file and update the vocabulary with the lemmas in that file"""
    file = open(path)
    for line in file.readlines():
        # This means that it's the start of a new utterance
        if line[0] == "*":
            # Nouns are always in title case in German
            for word in [w for w in re.split(r'[ _]',line.strip())[1:]
                         if not any(p in w for p in punctuation) and
                            not any(n in "0123456789" for n in w) and w == w.title()]:
                if word not in vocab:
                    vocab[word] = 0
                vocab[word] += 1
    file.close()

def read_celex(celex_path):
    """Read in the CELEX data and return a dictionary of compounds based on morphological parse"""
    compounds = {}
    file = open(f"{celex_path}/gml/gml.cd")
    for line in file.readlines():
        line = line.strip().split("\\")
        word = line[1]
        plus = line[8]
        if "+" in plus:
            compounds[word] = plus
    file.close()
    return compounds

def main(childes_path, celex_path, out_path):
    """The main function to extract the data"""
    np.random.seed(42)

    # Get all the .cha filepaths from German-CHILDES
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

    # Filter to just compounds
    print(f"Extracted {len(vocab)} nouns. Filtering to compounds...")
    celex = read_celex(celex_path)
    compounds = {}
    for k, v in sorted(vocab.items(), key=lambda x: x[1], reverse=True):
        # Check that it is a compound
        if k in celex:
            constituents = celex[k].split("+")
            # Noun+noun compounds -- each noun is in title case
            if len([k for k in constituents if k.title() == k]) == 2:
                e_interfixation = False
                i = 0
                while constituents[i].title() != constituents[i]:
                    i += 1
                first_constituent = constituents[i]
                e_interfixation = first_constituent[-1] == "e" or constituents[i] == "e" or constituents[-1][0] == "E"

                compounds[(k, celex[k], e_interfixation)] = v

    print(f"Found {len(compounds)} compounds. Writing out to {out_path}...")
    with open(out_path, "w") as f:
        for k, v in sorted(compounds.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{k[0]}\t{k[1]}\t{k[2]}\t{v}\n")
    f.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--childes", required=True, help="Path to German-CHILDES data")
    parser.add_argument("--celex", required=True, help="Path to CELEX data")
    parser.add_argument("--out", required=True, help = "Path to write output data to")
    args = parser.parse_args()
    main(args.childes, args.celex, args.out)