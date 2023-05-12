import sys


if __name__ == "__main__":
    path = sys.argv[1]
    vocab_size = int(sys.argv[2])
    out_path = f"{path}.kenlm.{sys.argv[3]}vocab"
    with open(path, "r") as f, open(out_path, "w") as fout:
        for index, line in enumerate(f):
            if index >= vocab_size:
                break
            fout.write(line.strip().split(" ")[0] + " ")
