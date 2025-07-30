# Copyright (C) 2025 Genome Research Ltd.

import numpy as np
import pytest
import struct

import py_crispr_analyser.utils as utils


class TestGetGuides:
    def test_when_guides_file_is_correct_with_matches(self, tmp_path):
        d = tmp_path / "test"
        d.mkdir()
        in_file = d / "guides.bin"
        in_file.write_bytes(
            struct.pack(
                "<BLQQQB30s30sBBBQQ",
                # start of file byte
                np.uint8(1),
                # file version
                np.uint(3),
                # metadata
                np.uint64(2),  # number of sequences
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
            )
        )
        in_file = open(in_file, "rb")
        assert np.array_equal(
            utils.get_guides(in_file),
            [
                np.uint64(0b111000001010111000001010111000001010111),
                np.uint64(0b1100000101011100000101011100000101011100),
            ],
        )

    def test_when_guides_size_and_metadata_number_disagree(
        self, tmp_path, capsys
    ):
        """Test that an exception is raised when the number_of_sequences in the
        metadata does not match the number of guides in the following array"""
        d = tmp_path / "test"
        d.mkdir()
        in_file = d / "guides.bin"
        in_file.write_bytes(
            struct.pack(
                "<BLQQQB30s30sBBBQQ",
                # start of file byte
                np.uint8(1),
                # file version
                np.uint(3),
                # metadata
                np.uint64(7),  # number of sequences
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
            )
        )
        in_file = open(in_file, "rb")
        with pytest.raises(ValueError) as excinfo:
            utils.get_guides(in_file)
        assert str(excinfo.value) == "Invalid number of guides"


class TestSequenceToBinaryEncoding:
    def test_when_pam_is_right(self):
        assert utils.sequence_to_binary_encoding(
            sequence="ACGT", pam_right=1
        ) == np.uint64(0b100011011)

    def test_with_pam_right_false(self):
        assert utils.sequence_to_binary_encoding(
            sequence="ACGT", pam_right=0
        ) == np.uint64(0b11011)

    def test_with_error_flag(self):
        assert (
            utils.sequence_to_binary_encoding(sequence="ACGN", pam_right=0)
            == utils.ERROR_STR
        )


def test_reverse_complement():
    assert utils.reverse_complement("ATCGN") == "NCGAT"


class TestCheckFileHeader:
    def test_when_version_is_3(self):
        header = struct.pack("<BL", 1, 3)
        try:
            utils.check_file_header(header)
        except Exception as e:
            pytest.fail(f"Unexpected exception: {e}")

    def test_raises_exception_when_version_is_wrong(self):
        header = struct.pack("<BL", 1, 4)
        with pytest.raises(ValueError) as excinfo:
            utils.check_file_header(header)
        assert str(excinfo.value) == "Invalid file version"

    def test_raises_exception_when_header_is_too_short(self):
        header = struct.pack("<B", 1)
        with pytest.raises(ValueError) as excinfo:
            utils.check_file_header(header)
        assert str(excinfo.value) == "Invalid file header length"

    def test_raises_exception_when_header_is_too_long(self):
        header = struct.pack("<BLB", 1, 3, 1)
        with pytest.raises(ValueError) as excinfo:
            utils.check_file_header(header)
        assert str(excinfo.value) == "Invalid file header length"


class TestGetFileMetadata:
    def test_when_metadata_is_correct(self):
        metadata = struct.pack(
            "<QQQB30s30s",
            1000,
            20,
            0,
            1,
            "Human".encode("utf-8"),
            "GRCh38".encode("utf-8"),
        )
        assert utils.get_file_metadata(metadata) == utils.Metadata(
            number_of_sequences=1000,
            sequence_length=20,
            offset=0,
            species_id=1,
            species_name="Human",
            assembly="GRCh38",
        )

    def test_raises_exception_when_metadata_is_too_short(self):
        metadata = struct.pack("<Q", 1000)
        with pytest.raises(ValueError) as excinfo:
            utils.get_file_metadata(metadata)
        assert str(excinfo.value) == "Invalid metadata length"

    def test_raises_exception_when_metadata_is_too_long(self):
        metadata = struct.pack(
            "<QQQQB30s30s",
            1000,
            20,
            0,
            1000,
            1,
            "Human".encode("utf-8"),
            "GRCh38".encode("utf-8"),
        )
        with pytest.raises(ValueError) as excinfo:
            utils.get_file_metadata(metadata)
        assert str(excinfo.value) == "Invalid metadata length"
