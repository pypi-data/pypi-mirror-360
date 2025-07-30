# Copyright (C) 2025 Genome Research Ltd.

import pytest
import numpy as np
import struct
import py_crispr_analyser.index as index


class TestParseRecord:
    def test_when_pam_right_is_true(self):
        assert index.parse_record(
            record="MT,13,ATCACCCTATTAACCACTCACGG,1,1",
            guide_length=20,
            pam_length=3,
        ) == ("ATCACCCTATTAACCACTCA", 1)

    def test_when_pam_right_is_false(self):
        assert index.parse_record(
            record="MT,13,ATCACCCTATTAACCACTCACGG,0,1",
            guide_length=20,
            pam_length=3,
        ) == ("ACCCTATTAACCACTCACGG", 0)

    def test_raises_exception_when_record_is_too_short(self, capsys):
        with pytest.raises(SystemExit):
            index.parse_record(
                record="MT,13,ATCACCCTATTAACCACTCACGG,1",
                guide_length=20,
                pam_length=3,
            )
        captured = capsys.readouterr()
        assert (
            captured.out == "Record 'MT,13,ATCACCCTATTAACCACTCACGG,1' "
            "contains 4 columns, expected 5\n"
        )

    def test_raises_exception_when_record_is_too_long(self, capsys):
        with pytest.raises(SystemExit):
            index.parse_record(
                record="MT,13,ATCACCCTATTAACCACTCACGG,1,1,1",
                guide_length=20,
                pam_length=3,
            )
        captured = capsys.readouterr()
        assert (
            captured.out == "Record 'MT,13,ATCACCCTATTAACCACTCACGG,1,1,1' "
            "contains 6 columns, expected 5\n"
        )

    def test_raises_exception_when_crispr_sequence_length_is_wrong(
        self, capsys
    ):
        with pytest.raises(SystemExit):
            index.parse_record(
                record="MT,13,ATCACCCTATTAACCACTCACGG,1,1",
                guide_length=20,
                pam_length=2,
            )
            captured = capsys.readouterr()
            assert (
                captured.out == "Record MT,13,ATCACCCTATTAACCACTCACGG,1,1 has "
                "sequence_length 23, expected 22\n"
            )


@pytest.fixture
def expected_binary_output():
    return struct.pack(
        "<BLQQQB30s30sBBBQQQQQQQQ",
        # start of file byte
        np.uint8(1),
        # file version
        np.uint(3),
        # metadata
        np.uint64(8),
        np.uint64(20),
        np.uint64(88),
        np.uint8(1),
        b"Human",
        b"GRCh38",
        # padding
        np.uint8(0),
        np.uint8(0),
        np.uint8(0),
        # array of sequences
        np.uint64(0b111000001010111000001010111000001010111),
        np.uint64(0b1100000101011100000101011100000101011100),
        np.uint64(0b10101110000010101110000010101110000),
        np.uint64(0b111000001010111000001010111000001010111),
        np.uint64(
            0b1111111111111111111111111111111111111111111111111111111111111111
        ),
        np.uint64(0b1100110101010001000100010100010001010100),
        np.uint64(0b100010001000101000100010101000100010001),
        np.uint64(0b1000100010100010001010100010001000101),
    )


@pytest.fixture
def csv_input_1():
    return """1,10003,ACCCTAACCCTAACCCTAACCCT,0,1
1,10004,CCCTAACCCTAACCCTAACCCTA,0,1
1,10005,CCTAACCCTAACCCTAACCCTAA,0,1
1,10009,ACCCTAACCCTAACCCTAACCCT,0,1
"""


@pytest.fixture
def csv_input_2():
    return """2,9981,NNNNNNNNNNNNNNNNNNNNCGT,1,1
2,10000,NCGTATCCCACACACCACACCCA,0,1
2,10005,TCCCACACACCACACCCACACAC,0,1
2,10006,CCCACACACCACACCCACACACC,0,1
"""


@pytest.fixture
def prepare_files(tmp_path, csv_input_1, csv_input_2):
    d = tmp_path / "test"
    d.mkdir()
    infile_1 = d / "test1.csv"
    infile_1.write_text(csv_input_1)
    infile_2 = d / "test2.csv"
    infile_2.write_text(csv_input_2)
    outfile = d / "test.bin"
    return infile_1, infile_2, outfile


def test_index(prepare_files, expected_binary_output):
    infile_1, infile_2, outfile = prepare_files
    index.index(
        inputfiles=[infile_1, infile_2],
        outputfile=outfile,
        species="Human",
        assembly="GRCh38",
        offset=88,
        species_id=1,
        guide_length=20,
        pam_length=3,
    )

    assert outfile.read_bytes() == expected_binary_output


def test_run(prepare_files, expected_binary_output):
    infile_1, infile_2, outfile = prepare_files
    args = [
        "-i",
        infile_1,
        "-i",
        infile_2,
        "-o",
        outfile,
        "-s",
        "Human",
        "-a",
        "GRCh38",
        "-f",
        "88",
        "-e",
        "1",
        "-g",
        "20",
        "-p",
        "3",
    ]
    index.run(args)

    assert outfile.read_bytes() == expected_binary_output
