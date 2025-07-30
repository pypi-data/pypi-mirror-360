import py_crispr_analyser.utils as utils
import py_crispr_analyser.align as align
import numpy as np

PAM_ON = np.left_shift(1, 40, dtype=np.uint64)
PAM_OFF = np.invert(PAM_ON, dtype=np.uint64)

def test():
    print("PAM_ON: ", bin(PAM_ON))
    print("PAM_OFF: ", bin(PAM_OFF))

    seq1 = "ACGT"
    seq2 = "ACTT"
    seq3 = "TCTT"

    print("seq1: ", seq1)
    print("seq2: ", seq2)
    print("seq3: ", seq3)

    seq1_bin = utils.sequence_to_binary_encoding(seq1, 1)
    seq2_bin = utils.sequence_to_binary_encoding(seq2, 1)
    seq3_bin = utils.sequence_to_binary_encoding(seq3, 1)

    print("seq1: ", bin(seq1_bin))
    print("seq2: ", bin(seq2_bin))
    print("seq3: ", bin(seq3_bin))

    match1 = seq1_bin ^ seq2_bin
    match2 = seq1_bin ^ seq3_bin

    print("match1: ", bin(match1))
    print("match2: ", bin(match2))

    popcount(match2 & PAM_OFF)
    count(match2 & PAM_OFF)


def popcount(x):
    print(f"match & PAM: {bin(x)}")
    x = np.uint64((x | (x >> 1)))
    print(f"x | x >> 1: {bin(x)}")
    x = x & 0x5555555555555555
    print(f"x & 0x5555555555555555: {bin(x)}")
    x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    print(f"x: {bin(x)}")
    x = (x + (x >> 4)) & 0x0F0F0F0F0F0F0F0F
    print("popcount: ", (0x0101010101010101 * x) >> 56)

def count(x):
    x = (x | (x >> 1)) & 0x5555555555555555
    print("count: ", np.bitwise_count(x))

if __name__ == "__main__":
    test()

