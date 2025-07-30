# Copyright (C) 2025 Genome Research Ltd.

import numpy as np
from numba import cuda
import pytest
import py_crispr_analyser.align as align


@pytest.fixture
def query_sequence():
    # AAAACTGGAAACTGGTTCTC pam right
    return np.uint64(0b10000000001111010000000011110101111011101)


@pytest.fixture
def reverse_query_sequence():
    # GAGAACCAGTTTCCAGTTTT pam left
    return np.uint64(0b1000100000010100101111110101001011111111)


@pytest.fixture
def expected_guides():
    return [
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79,
        80,
        81,
        82,
        83,
        84,
        85,
        86,
        87,
        88,
        89,
        90,
        91,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111,
        112,
        113,
        114,
        115,
        116,
        117,
        118,
        119,
        120,
        121,
        122,
        123,
        124,
        125,
        126,
        127,
        128,
        129,
        130,
        131,
        132,
        133,
        134,
        135,
        136,
        137,
        138,
        139,
        140,
        141,
        142,
        143,
        144,
        145,
        146,
        147,
        148,
        149,
        150,
        151,
        152,
        153,
        154,
        155,
        156,
        157,
        158,
        159,
        160,
        161,
        162,
        163,
        164,
        165,
        166,
        167,
        168,
        169,
        170,
        171,
        172,
        173,
        174,
        175,
        176,
        177,
        178,
        179,
        180,
        181,
        182,
        183,
        184,
        185,
        186,
        187,
        188,
        189,
        190,
        191,
        192,
        193,
        194,
        195,
        196,
        197,
        198,
        199,
        200,
        201,
        202,
        203,
        204,
        205,
        206,
        207,
        208,
        209,
        210,
        211,
        212,
        213,
        214,
        215,
        216,
        217,
        218,
        219,
        220,
        221,
        222,
        223,
        224,
        225,
        226,
        227,
        228,
        229,
        230,
        231,
        232,
        233,
        234,
        235,
        236,
        237,
        238,
        239,
        240,
        241,
        242,
        243,
        244,
        245,
        246,
        247,
        248,
        249,
        250,
        251,
        252,
        253,
        254,
        255,
        256,
        257,
        258,
        259,
        260,
        261,
        262,
        263,
        264,
        265,
        266,
        267,
        268,
        269,
        270,
        271,
        272,
        273,
        274,
        275,
        276,
        277,
        278,
        279,
        280,
        281,
        282,
        283,
        284,
        285,
        286,
        287,
        288,
        289,
        290,
        291,
        292,
        293,
        294,
        295,
        296,
        297,
        298,
        299,
        300,
        301,
        302,
        303,
        304,
        305,
        306,
        307,
        308,
        309,
        310,
        311,
        312,
        313,
        314,
        315,
        316,
        317,
        318,
        319,
        320,
        321,
        322,
        323,
        324,
        325,
        326,
        327,
        328,
        330,
        331,
        332,
        333,
        334,
        335,
        336,
        337,
        338,
        339,
        340,
        341,
        342,
        343,
        344,
        345,
        346,
        347,
        348,
        349,
        350,
        351,
        352,
        353,
        354,
        355,
        356,
        357,
        358,
        359,
        360,
        361,
        362,
        363,
        364,
        365,
        366,
        367,
        368,
        369,
        370,
        371,
        372,
        373,
        374,
        375,
        376,
        377,
        378,
        379,
        380,
        381,
        382,
        383,
        384,
        385,
        386,
        387,
        388,
        389,
        390,
        391,
    ]


def test_find_off_targets(
    guide_list, query_sequence, reverse_query_sequence, expected_guides
):
    """The expected output using CPU based on output from:
    https://github.com/htgt/crispacuda and
    https://github.com/htgt/CRISPR-Analyser."""
    summary, off_target_ids = align.find_off_targets(
        guide_list, query_sequence, reverse_query_sequence, 0
    )
    assert summary == [2, 0, 1, 36, 350]
    assert off_target_ids == expected_guides


@pytest.mark.skipif(
    cuda.is_available() is False, reason="CUDA is not available"
)
def test_find_off_targets_kernel(
    guide_list, query_sequence, reverse_query_sequence, expected_guides
):
    """The expected output using GPU based on output from:
    https://github.com/htgt/crispacuda and
    https://github.com/htgt/CRISPR-Analyser."""
    threads_per_block = 32
    blocks_per_grid = 392
    device_guides = cuda.to_device(guide_list)
    summary = np.zeros(5, dtype=np.uint32)
    off_target_ids_idx = np.zeros(1, dtype=np.uint32)
    off_target_ids = np.zeros(2000, dtype=np.uint32)
    device_summary = cuda.to_device(summary)
    device_off_target_ids_idx = cuda.to_device(off_target_ids_idx)
    device_off_target_ids = cuda.to_device(off_target_ids)
    align.find_off_targets_kernel[blocks_per_grid, threads_per_block](
        device_guides,
        query_sequence,
        reverse_query_sequence,
        device_summary,
        device_off_target_ids_idx,
        device_off_target_ids,
        0,
    )
    host_summary = device_summary.copy_to_host()
    host_off_target_ids = np.trim_zeros(device_off_target_ids.copy_to_host())
    np.testing.assert_array_equal(
        host_summary, np.array([2, 0, 1, 36, 350], dtype=np.uint32)
    )
    np.testing.assert_array_equal(
        np.sort(host_off_target_ids), np.array(expected_guides, dtype=np.uint32)
    )


def test_pop_count(query_sequence):
    # "AAAACTGGTGCCTGGTTCTC" pam right
    test_seq = np.uint64(0b10000000001111010111001011110101111011101)
    match = test_seq ^ query_sequence
    match_count = align._pop_count(match & align.PAM_OFF)
    assert match_count == 3


def test_reverse_complement_binary(query_sequence, reverse_query_sequence):
    assert (
        align.reverse_complement_binary(query_sequence, 20)
        == reverse_query_sequence
    )


def test_run(tmp_path, guides_file, capsys):
    expected_start = "101\t1"
    expected_ids = (
        "{6,8,9,10,14,18,30,33,56,78,86,87,92,101,112,116,128,151,"
        "154,155,157,160,172,176,197,200,204,207,218,219,230,235,247,249,251,"
        "269,293,305,328,337,340,349,376,379,391}"
    )
    expected_off_targets = "{0: 27, 1: 2, 2: 4, 3: 1, 4: 11}"
    args = [
        "--ifile",
        guides_file,
        "101",
    ]
    align.run(args)
    captured = capsys.readouterr()
    assert expected_start in captured.out
    assert expected_ids in captured.out
    assert expected_off_targets in captured.out
