import sys


pl_data = []
with open(sys.argv[1], "r") as f:
    pl_data.extend(line.strip() for line in f)
pl_data = set(pl_data)

with open(f"{sys.argv[1]}.unique", "w") as f:
    for elem in pl_data:
        f.write(elem + "\n")
