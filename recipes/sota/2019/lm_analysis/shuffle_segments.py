import os
import random
import sys
from multiprocessing import Pool

import sox


align_file = sys.argv[1]
output_dir = sys.argv[2]

lines = []
with open(align_file) as fin:
    lines = fin.readlines()

N_THREADS = 40
MIN_SIL_LENGTH = 0.13
TOLERANCE = 0.04


def process(parameters):
    tid, n_samples = parameters
    output_list = f"{output_dir}dev-other.{tid}.lst"

    with open(output_list, "w") as fout:
        for i in range(tid * n_samples, min(len(lines), n_samples * (tid + 1))):
            line = lines[i]
            sp = line.split("\t")
            filename = sp[0]
            # print(filename)
            # duration = sox.file_info.duration(filename)

            alignments = sp[1].strip().split("\\n")

            # Parse the alignments
            chunk_starts = [0]
            chunk_ends = []
            words = []

            cur_words = []
            cur_end = 0
            for i, alignment in enumerate(alignments):
                sp = alignment.split()
                begin = float(sp[2])
                length = float(sp[3])
                word = sp[4]

                cur_end = begin + length

                if i == 0:
                    continue

                if word == "$":
                    if length > MIN_SIL_LENGTH:
                        chunk_ends.append(cur_end - TOLERANCE)
                        chunk_starts.append(cur_end - TOLERANCE)
                        words.append(" ".join(cur_words))
                        cur_words = []
                    continue

                cur_words.append(word)

            if len(cur_words) > 0:
                chunk_ends.append(cur_end)
                words.append(" ".join(cur_words))
            else:
                chunk_starts.pop()
            # print(duration)
            # print(chunk_starts)
            # print(chunk_ends)
            # print(words)

            # Split the audios
            order = list(range(len(chunk_starts)))
            random.shuffle(order)

            new_target = " ".join([words[i] for i in order])
            new_audio_path = output_dir + filename.split("/")[-1]
            fout.write(
                f"{new_audio_path}\t{new_audio_path}\t{chunk_ends[-1] * 1000}\t{new_target}\n"
            )

            if len(chunk_starts) == 1:
                os.system(f"cp {filename} {output_dir}")
                continue

            paths = []
            for i in order:
                sox_tfm = sox.Transformer()
                sox_tfm.set_output_format(
                    file_type="flac", encoding="signed-integer", bits=16, rate=16000
                )
                sox_tfm.trim(chunk_starts[i], chunk_ends[i])
                new_path = f"/tmp/{tid}_{i}.flac"
                sox_tfm.build(filename, new_path)
                paths.append(new_path)

            # Combine them
            sox_comb = sox.Combiner()
            sox_comb.build(list(paths), new_audio_path, "concatenate")


if __name__ == "__main__":
    n_sample_per_thread = len(lines) // N_THREADS + 1
    print(
        f"Spreading {N_THREADS} threads with {n_sample_per_thread} samples in each"
    )

    pool = Pool(N_THREADS)
    pool.map(process, zip(list(range(N_THREADS)), [n_sample_per_thread] * N_THREADS))
    pool.close()
    pool.join()
