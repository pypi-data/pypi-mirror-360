# Copyright (C) 2025 Genome Research Ltd.

import numpy as np
import pytest
import struct

import py_crispr_analyser.search as search


@pytest.fixture
def guides_array_with_matches():
    return np.array(
        [
            np.uint64(0b10000000001111010000000011110101111011101),
            np.uint64(0b10000011110100000000111101011110111011110),
            np.uint64(0b1000100000010100101111110101001011111111),
            np.uint64(0b11000100000010100101111110101001011111111),
            np.uint64(0b1100110101010001000100010100010001010100),
            np.uint64(0b10111111010100101111111111100111111101),
            np.uint64(0b11000100000010100101111110101001011111111),
        ]
    )


@pytest.fixture
def guides_array_with_no_matches():
    ERROR_STR = np.uint64(0xFFFFFFFFFFFFFFFF)
    return np.array(
        [
            np.uint64(0b111000001010111000001010111000001010111),
            np.uint64(0b1100000101011100000101011100000101011100),
            np.uint64(0b10101110000010101110000010101110000),
            np.uint64(0b111000001010111000001010111000001010111),
            ERROR_STR,
            np.uint64(0b1100110101010001000100010100010001010100),
            np.uint64(0b100010001000101000100010101000100010001),
        ]
    )


@pytest.fixture
def guides_with_matches_file(tmp_path, guides_array_with_matches):
    d = tmp_path / "test"
    d.mkdir()
    in_file = d / "crisprs.bin"
    in_file.write_bytes(
        struct.pack(
            "<BLQQQB30s30sBBBQQQQQQQ",
            # start of file byte
            np.uint8(1),
            # file version
            np.uint(3),
            # metadata
            np.uint64(7),
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
            *guides_array_with_matches,
        )
    )
    return in_file


@pytest.fixture
def guides_with_no_matches_file(tmp_path, guides_array_with_no_matches):
    d = tmp_path / "test"
    d.mkdir()
    in_file = d / "crisprs.bin"
    in_file.write_bytes(
        struct.pack(
            "<BLQQQB30s30sBBBQQQQQQQ",
            # start of file byte
            np.uint8(1),
            # file version
            np.uint(3),
            # metadata
            np.uint64(7),
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
            *guides_array_with_no_matches,
        )
    )
    return in_file


class TestSearch:
    def test_multiple_sequences_are_found(self, guides_array_with_matches):
        assert search.search(
            guides_array_with_matches, "AAAACTGGAAACTGGTTCTC"
        ) == [1, 3]

    def test_no_sequences_are_found(self, guides_array_with_no_matches):
        assert (
            search.search(guides_array_with_no_matches, "AAAACTGGAAACTGGTTCTC")
            == []
        )


class TestRun:
    def test_multiple_sequences_are_found(
        self, guides_with_matches_file, capsys
    ):
        """Test that the run function prints the correct output when multiple
        sequences are found given an offset"""
        args = [
            "-i",
            guides_with_matches_file,
            "-s",
            "AAAACTGGAAACTGGTTCTC",
        ]
        search.run(args)
        captured = capsys.readouterr()
        assert "Found 2 exact matches" in captured.err
        assert "\t89\n\t91" in captured.out

    def test_no_sequences_are_found(self, guides_with_no_matches_file, capsys):
        args = [
            "-i",
            guides_with_no_matches_file,
            "-s",
            "AAAACTGGAAACTGGTTCTC",
        ]
        search.run(args)
        captured = capsys.readouterr()
        assert "Found 0 exact matches" in captured.err
