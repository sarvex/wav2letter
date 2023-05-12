import sys

prev_line = "hello world"
for line in sys.stdin:
    line = line.strip()
    if prev_line != "":
        print(line, end=" ")
    else:
        print("\n" + line, end=" ")

    prev_line = line
