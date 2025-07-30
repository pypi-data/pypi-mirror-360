# Copyright (C) 2025 Genome Research Ltd.

import pytest
import py_crispr_analyser.gather as gather


class TestMatchPam:
    def test_N_in_pam_sequence(self):
        """Test that N acts like a wildcard in the PAM sequence"""
        assert (
            gather.match_pam(
                dna_sequence="ATCGA", pam_sequence="GN", pam_on_right=True
            )
            is True
        )
        assert (
            gather.match_pam(
                dna_sequence="ATCGA", pam_sequence="AN", pam_on_right=True
            )
            is False
        )

    def test_pam_on_right(self):
        """Test that matching is done on the right PAM sequence"""
        assert (
            gather.match_pam(
                dna_sequence="ATCGA", pam_sequence="GN", pam_on_right=True
            )
            is True
        )
        assert (
            gather.match_pam(
                dna_sequence="ATCGA", pam_sequence="AT", pam_on_right=True
            )
            is False
        )
        assert (
            gather.match_pam(
                dna_sequence="ATCGA", pam_sequence="GA", pam_on_right=True
            )
            is True
        )

    def test_pam_on_left(self):
        """Test that matching is done on the left PAM sequence
        with reverse_complement"""
        assert (
            gather.match_pam(
                dna_sequence="ATCGA", pam_sequence="GN", pam_on_right=False
            )
            is False
        )
        assert (
            gather.match_pam(
                dna_sequence="ATCGA", pam_sequence="GN", pam_on_right=False
            )
            is False
        )
        assert (
            gather.match_pam(
                dna_sequence="ATCGA", pam_sequence="AT", pam_on_right=False
            )
            is True
        )

    def test_non_ACGT_character_in_dna_sequence(self):
        """Test that we don't support non-ACGT characters in
        the PAM sequence"""
        assert (
            gather.match_pam(
                dna_sequence="ATCAN", pam_sequence="AN", pam_on_right=True
            )
            is False
        )
        assert (
            gather.match_pam(
                dna_sequence="NTCGA", pam_sequence="AN", pam_on_right=False
            )
            is False
        )
        assert (
            gather.match_pam(
                dna_sequence="ATNGA", pam_sequence="AN", pam_on_right=False
            )
            is True
        )


@pytest.fixture
def single_chromosome_fasta():
    """Test fixture for a single chromosome fasta file"""
    return """>MT dna:chromosome chromosome:GRCh38:MT:1:16569:1 REF
GATCACAGGTCTATCACCCTATTAACCACTCACGGGAGCTCTCCATGCATTTGGTATTTT
CGTCTGGGGGGTATGCACGCGATAGCATTGCGAGACGCTGGAGCCGGAGCACCCTATGTC
GCAGTATCTGTCTTTGATTCCTGCCTCATCCTATTATTTATCGCACCTACGTTCAATATT"""


@pytest.fixture
def expected_csv_with_ngg_pam_legacy():
    """Test fixture for output CSV with 'NGG' PAM in Legacy format"""
    return """MT,13,ATCACCCTATTAACCACTCACGG,1,1
MT,14,TCACCCTATTAACCACTCACGGG,1,1
MT,17,CCCTATTAACCACTCACGGGAGC,0,1
MT,18,CCTATTAACCACTCACGGGAGCT,0,1
MT,26,CCACTCACGGGAGCTCTCCATGC,0,1
MT,32,ACGGGAGCTCTCCATGCATTTGG,1,1
MT,43,CCATGCATTTGGTATTTTCGTCT,0,1
MT,45,ATGCATTTGGTATTTTCGTCTGG,1,1
MT,46,TGCATTTGGTATTTTCGTCTGGG,1,1
MT,47,GCATTTGGTATTTTCGTCTGGGG,1,1
MT,48,CATTTGGTATTTTCGTCTGGGGG,1,1
MT,49,ATTTGGTATTTTCGTCTGGGGGG,1,1
MT,79,GCGATAGCATTGCGAGACGCTGG,1,1
MT,85,GCATTGCGAGACGCTGGAGCCGG,1,1
MT,104,CCGGAGCACCCTATGTCGCAGTA,0,1
MT,112,CCCTATGTCGCAGTATCTGTCTT,0,1
MT,113,CCTATGTCGCAGTATCTGTCTTT,0,1
MT,140,CCTGCCTCATCCTATTATTTATC,0,1
MT,144,CCTCATCCTATTATTTATCGCAC,0,1
MT,150,CCTATTATTTATCGCACCTACGT,0,1
"""


@pytest.fixture
def expected_csv_with_ngg_pam_non_legacy():
    """Test fixture for output CSV with 'NGG' PAM in Non-Legacy format"""
    return """MT,13,ATCACCCTATTAACCACTCACGG,1
MT,14,TCACCCTATTAACCACTCACGGG,1
MT,17,CCCTATTAACCACTCACGGGAGC,0
MT,18,CCTATTAACCACTCACGGGAGCT,0
MT,26,CCACTCACGGGAGCTCTCCATGC,0
MT,32,ACGGGAGCTCTCCATGCATTTGG,1
MT,43,CCATGCATTTGGTATTTTCGTCT,0
MT,45,ATGCATTTGGTATTTTCGTCTGG,1
MT,46,TGCATTTGGTATTTTCGTCTGGG,1
MT,47,GCATTTGGTATTTTCGTCTGGGG,1
MT,48,CATTTGGTATTTTCGTCTGGGGG,1
MT,49,ATTTGGTATTTTCGTCTGGGGGG,1
MT,79,GCGATAGCATTGCGAGACGCTGG,1
MT,85,GCATTGCGAGACGCTGGAGCCGG,1
MT,104,CCGGAGCACCCTATGTCGCAGTA,0
MT,112,CCCTATGTCGCAGTATCTGTCTT,0
MT,113,CCTATGTCGCAGTATCTGTCTTT,0
MT,140,CCTGCCTCATCCTATTATTTATC,0
MT,144,CCTCATCCTATTATTTATCGCAC,0
MT,150,CCTATTATTTATCGCACCTACGT,0
"""


@pytest.fixture
def expected_csv_with_ngn_pam_legacy():
    """Test fixture for ouput with 'NGN' PAM in Legacy format"""
    return """MT,3,TCACAGGTCTATCACCCTATTAA,0,1
MT,5,ACAGGTCTATCACCCTATTAACC,0,1
MT,10,TCTATCACCCTATTAACCACTCA,0,1
MT,13,ATCACCCTATTAACCACTCACGG,1,1
MT,14,TCACCCTATTAACCACTCACGGG,0,1
MT,14,TCACCCTATTAACCACTCACGGG,1,1
MT,15,CACCCTATTAACCACTCACGGGA,1,1
MT,16,ACCCTATTAACCACTCACGGGAG,0,1
MT,17,CCCTATTAACCACTCACGGGAGC,0,1
MT,17,CCCTATTAACCACTCACGGGAGC,1,1
MT,18,CCTATTAACCACTCACGGGAGCT,0,1
MT,25,ACCACTCACGGGAGCTCTCCATG,0,1
MT,26,CCACTCACGGGAGCTCTCCATGC,0,1
MT,26,CCACTCACGGGAGCTCTCCATGC,1,1
MT,28,ACTCACGGGAGCTCTCCATGCAT,0,1
MT,30,TCACGGGAGCTCTCCATGCATTT,0,1
MT,32,ACGGGAGCTCTCCATGCATTTGG,0,1
MT,32,ACGGGAGCTCTCCATGCATTTGG,1,1
MT,33,CGGGAGCTCTCCATGCATTTGGT,1,1
MT,38,GCTCTCCATGCATTTGGTATTTT,0,1
MT,40,TCTCCATGCATTTGGTATTTTCG,0,1
MT,41,CTCCATGCATTTGGTATTTTCGT,1,1
MT,42,TCCATGCATTTGGTATTTTCGTC,0,1
MT,43,CCATGCATTTGGTATTTTCGTCT,0,1
MT,45,ATGCATTTGGTATTTTCGTCTGG,1,1
MT,46,TGCATTTGGTATTTTCGTCTGGG,1,1
MT,47,GCATTTGGTATTTTCGTCTGGGG,0,1
MT,47,GCATTTGGTATTTTCGTCTGGGG,1,1
MT,48,CATTTGGTATTTTCGTCTGGGGG,1,1
MT,49,ATTTGGTATTTTCGTCTGGGGGG,1,1
MT,50,TTTGGTATTTTCGTCTGGGGGGT,1,1
MT,54,GTATTTTCGTCTGGGGGGTATGC,1,1
MT,58,TTTCGTCTGGGGGGTATGCACGC,1,1
MT,60,TCGTCTGGGGGGTATGCACGCGA,0,1
MT,60,TCGTCTGGGGGGTATGCACGCGA,1,1
MT,63,TCTGGGGGGTATGCACGCGATAG,0,1
MT,64,CTGGGGGGTATGCACGCGATAGC,1,1
MT,69,GGGTATGCACGCGATAGCATTGC,1,1
MT,71,GTATGCACGCGATAGCATTGCGA,1,1
MT,73,ATGCACGCGATAGCATTGCGAGA,1,1
MT,75,GCACGCGATAGCATTGCGAGACG,0,1
MT,76,CACGCGATAGCATTGCGAGACGC,1,1
MT,77,ACGCGATAGCATTGCGAGACGCT,0,1
MT,79,GCGATAGCATTGCGAGACGCTGG,0,1
MT,79,GCGATAGCATTGCGAGACGCTGG,1,1
MT,80,CGATAGCATTGCGAGACGCTGGA,1,1
MT,82,ATAGCATTGCGAGACGCTGGAGC,1,1
MT,85,GCATTGCGAGACGCTGGAGCCGG,0,1
MT,85,GCATTGCGAGACGCTGGAGCCGG,1,1
MT,86,CATTGCGAGACGCTGGAGCCGGA,1,1
MT,88,TTGCGAGACGCTGGAGCCGGAGC,1,1
MT,90,GCGAGACGCTGGAGCCGGAGCAC,0,1
MT,95,ACGCTGGAGCCGGAGCACCCTAT,0,1
MT,97,GCTGGAGCCGGAGCACCCTATGT,0,1
MT,97,GCTGGAGCCGGAGCACCCTATGT,1,1
MT,100,GGAGCCGGAGCACCCTATGTCGC,1,1
MT,103,GCCGGAGCACCCTATGTCGCAGT,0,1
MT,103,GCCGGAGCACCCTATGTCGCAGT,1,1
MT,104,CCGGAGCACCCTATGTCGCAGTA,0,1
MT,109,GCACCCTATGTCGCAGTATCTGT,0,1
MT,109,GCACCCTATGTCGCAGTATCTGT,1,1
MT,111,ACCCTATGTCGCAGTATCTGTCT,0,1
MT,112,CCCTATGTCGCAGTATCTGTCTT,0,1
MT,113,CCTATGTCGCAGTATCTGTCTTT,0,1
MT,115,TATGTCGCAGTATCTGTCTTTGA,1,1
MT,119,TCGCAGTATCTGTCTTTGATTCC,0,1
MT,121,GCAGTATCTGTCTTTGATTCCTG,0,1
MT,122,CAGTATCTGTCTTTGATTCCTGC,1,1
MT,127,TCTGTCTTTGATTCCTGCCTCAT,0,1
MT,131,TCTTTGATTCCTGCCTCATCCTA,0,1
MT,139,TCCTGCCTCATCCTATTATTTAT,0,1
MT,140,CCTGCCTCATCCTATTATTTATC,0,1
MT,142,TGCCTCATCCTATTATTTATCGC,1,1
MT,143,GCCTCATCCTATTATTTATCGCA,0,1
MT,144,CCTCATCCTATTATTTATCGCAC,0,1
MT,146,TCATCCTATTATTTATCGCACCT,0,1
MT,149,TCCTATTATTTATCGCACCTACG,0,1
MT,150,CCTATTATTTATCGCACCTACGT,0,1
MT,150,CCTATTATTTATCGCACCTACGT,1,1
"""


@pytest.fixture
def expected_csv_with_ngn_pam_non_legacy():
    """Test fixture for ouput with 'NGN' PAM in Non-Legacy format"""
    return """MT,3,TCACAGGTCTATCACCCTATTAA,0
MT,5,ACAGGTCTATCACCCTATTAACC,0
MT,10,TCTATCACCCTATTAACCACTCA,0
MT,13,ATCACCCTATTAACCACTCACGG,1
MT,14,TCACCCTATTAACCACTCACGGG,0
MT,14,TCACCCTATTAACCACTCACGGG,1
MT,15,CACCCTATTAACCACTCACGGGA,1
MT,16,ACCCTATTAACCACTCACGGGAG,0
MT,17,CCCTATTAACCACTCACGGGAGC,0
MT,17,CCCTATTAACCACTCACGGGAGC,1
MT,18,CCTATTAACCACTCACGGGAGCT,0
MT,25,ACCACTCACGGGAGCTCTCCATG,0
MT,26,CCACTCACGGGAGCTCTCCATGC,0
MT,26,CCACTCACGGGAGCTCTCCATGC,1
MT,28,ACTCACGGGAGCTCTCCATGCAT,0
MT,30,TCACGGGAGCTCTCCATGCATTT,0
MT,32,ACGGGAGCTCTCCATGCATTTGG,0
MT,32,ACGGGAGCTCTCCATGCATTTGG,1
MT,33,CGGGAGCTCTCCATGCATTTGGT,1
MT,38,GCTCTCCATGCATTTGGTATTTT,0
MT,40,TCTCCATGCATTTGGTATTTTCG,0
MT,41,CTCCATGCATTTGGTATTTTCGT,1
MT,42,TCCATGCATTTGGTATTTTCGTC,0
MT,43,CCATGCATTTGGTATTTTCGTCT,0
MT,45,ATGCATTTGGTATTTTCGTCTGG,1
MT,46,TGCATTTGGTATTTTCGTCTGGG,1
MT,47,GCATTTGGTATTTTCGTCTGGGG,0
MT,47,GCATTTGGTATTTTCGTCTGGGG,1
MT,48,CATTTGGTATTTTCGTCTGGGGG,1
MT,49,ATTTGGTATTTTCGTCTGGGGGG,1
MT,50,TTTGGTATTTTCGTCTGGGGGGT,1
MT,54,GTATTTTCGTCTGGGGGGTATGC,1
MT,58,TTTCGTCTGGGGGGTATGCACGC,1
MT,60,TCGTCTGGGGGGTATGCACGCGA,0
MT,60,TCGTCTGGGGGGTATGCACGCGA,1
MT,63,TCTGGGGGGTATGCACGCGATAG,0
MT,64,CTGGGGGGTATGCACGCGATAGC,1
MT,69,GGGTATGCACGCGATAGCATTGC,1
MT,71,GTATGCACGCGATAGCATTGCGA,1
MT,73,ATGCACGCGATAGCATTGCGAGA,1
MT,75,GCACGCGATAGCATTGCGAGACG,0
MT,76,CACGCGATAGCATTGCGAGACGC,1
MT,77,ACGCGATAGCATTGCGAGACGCT,0
MT,79,GCGATAGCATTGCGAGACGCTGG,0
MT,79,GCGATAGCATTGCGAGACGCTGG,1
MT,80,CGATAGCATTGCGAGACGCTGGA,1
MT,82,ATAGCATTGCGAGACGCTGGAGC,1
MT,85,GCATTGCGAGACGCTGGAGCCGG,0
MT,85,GCATTGCGAGACGCTGGAGCCGG,1
MT,86,CATTGCGAGACGCTGGAGCCGGA,1
MT,88,TTGCGAGACGCTGGAGCCGGAGC,1
MT,90,GCGAGACGCTGGAGCCGGAGCAC,0
MT,95,ACGCTGGAGCCGGAGCACCCTAT,0
MT,97,GCTGGAGCCGGAGCACCCTATGT,0
MT,97,GCTGGAGCCGGAGCACCCTATGT,1
MT,100,GGAGCCGGAGCACCCTATGTCGC,1
MT,103,GCCGGAGCACCCTATGTCGCAGT,0
MT,103,GCCGGAGCACCCTATGTCGCAGT,1
MT,104,CCGGAGCACCCTATGTCGCAGTA,0
MT,109,GCACCCTATGTCGCAGTATCTGT,0
MT,109,GCACCCTATGTCGCAGTATCTGT,1
MT,111,ACCCTATGTCGCAGTATCTGTCT,0
MT,112,CCCTATGTCGCAGTATCTGTCTT,0
MT,113,CCTATGTCGCAGTATCTGTCTTT,0
MT,115,TATGTCGCAGTATCTGTCTTTGA,1
MT,119,TCGCAGTATCTGTCTTTGATTCC,0
MT,121,GCAGTATCTGTCTTTGATTCCTG,0
MT,122,CAGTATCTGTCTTTGATTCCTGC,1
MT,127,TCTGTCTTTGATTCCTGCCTCAT,0
MT,131,TCTTTGATTCCTGCCTCATCCTA,0
MT,139,TCCTGCCTCATCCTATTATTTAT,0
MT,140,CCTGCCTCATCCTATTATTTATC,0
MT,142,TGCCTCATCCTATTATTTATCGC,1
MT,143,GCCTCATCCTATTATTTATCGCA,0
MT,144,CCTCATCCTATTATTTATCGCAC,0
MT,146,TCATCCTATTATTTATCGCACCT,0
MT,149,TCCTATTATTTATCGCACCTACG,0
MT,150,CCTATTATTTATCGCACCTACGT,0
MT,150,CCTATTATTTATCGCACCTACGT,1
"""


@pytest.fixture
def multiple_chromasomes_fasta():
    """Test that we can run with a fasta file with multiple chromosomes"""
    return """>MT dna:chromosome chromosome:GRCh38:MT:1:16569:1 REF
GATCACAGGTCTATCACCCTATTAACCACTCACGGGAGCTCTCCATGCATTTGGTATTTT
>X dna:chromosome chromosome:GRCh38:X:1:156040895:1 REF
ACAGGCGAACATACTTACTAAAGTGTGTTAATTAATTAATGCTTGTAGGACATAATAATA"""


@pytest.fixture
def expected_csv_with_multiple_chromosomes_legacy():
    return """MT,13,ATCACCCTATTAACCACTCACGG,1,1
MT,14,TCACCCTATTAACCACTCACGGG,1,1
MT,17,CCCTATTAACCACTCACGGGAGC,0,1
MT,18,CCTATTAACCACTCACGGGAGCT,0,1
MT,26,CCACTCACGGGAGCTCTCCATGC,0,1
MT,32,ACGGGAGCTCTCCATGCATTTGG,1,1
X,27,GTTAATTAATTAATGCTTGTAGG,1,1
"""


@pytest.fixture
def expected_csv_with_multiple_chromosomes_non_legacy():
    return """MT,13,ATCACCCTATTAACCACTCACGG,1
MT,14,TCACCCTATTAACCACTCACGGG,1
MT,17,CCCTATTAACCACTCACGGGAGC,0
MT,18,CCTATTAACCACTCACGGGAGCT,0
MT,26,CCACTCACGGGAGCTCTCCATGC,0
MT,32,ACGGGAGCTCTCCATGCATTTGG,1
X,27,GTTAATTAATTAATGCTTGTAGG,1
"""


class TestRun:
    """Test the command line run function"""

    def test_with_ngg_pam(
        self, tmp_path, single_chromosome_fasta, expected_csv_with_ngg_pam_legacy
    ):
        """Test that we can run the script with NGG PAM""",
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(single_chromosome_fasta)
        outfile = d / "test.csv"
        args = ["-i", infile, "-o", outfile, "-p", "NGG"]
        gather.run(args)
        assert outfile.read_text() == expected_csv_with_ngg_pam_legacy

    def test_with_ngn_pam(
        self, tmp_path, single_chromosome_fasta, expected_csv_with_ngn_pam_legacy
    ):
        """Test that we can run the script with NGN PAM"""
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(single_chromosome_fasta)
        outfile = d / "test.csv"
        args = ["-i", infile, "-o", outfile, "-p", "NGN"]
        gather.run(args)
        assert outfile.read_text() == expected_csv_with_ngn_pam_legacy

    def test_with_multiple_chromosomes(
        self,
        tmp_path,
        multiple_chromasomes_fasta,
        expected_csv_with_multiple_chromosomes_legacy,
    ):
        """Test that we can run the script with multiple chromosomes"""
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(multiple_chromasomes_fasta)
        outfile = d / "test.csv"
        args = ["-i", infile, "-o", outfile, "-p", "NGG"]
        gather.run(args)
        assert outfile.read_text() == expected_csv_with_multiple_chromosomes_legacy


class TestGather:
    """Test the gather function"""

    def test_with_ngg_pam_legacy(
        self, tmp_path, single_chromosome_fasta, expected_csv_with_ngg_pam_legacy
    ):
        """Test that we can run the script with NGG PAM in legacy mode"""
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(single_chromosome_fasta)
        outfile = d / "test.csv"
        gather.gather(
            inputfile=infile,
            outputfile=outfile,
            pam="NGG",
            verbose=False,
            legacy_mode=True,
        )
        assert outfile.read_text() == expected_csv_with_ngg_pam_legacy

    def test_with_ngg_pam_non_legacy(
        self, tmp_path, single_chromosome_fasta, expected_csv_with_ngg_pam_non_legacy
    ):
        """Test that we can run the script with NGG PAM in legacy mode"""
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(single_chromosome_fasta)
        outfile = d / "test.csv"
        gather.gather(
            inputfile=infile,
            outputfile=outfile,
            pam="NGG",
            verbose=False,
            legacy_mode=False,
        )
        assert outfile.read_text() == expected_csv_with_ngg_pam_non_legacy

    def test_with_ngn_pam_legacy(
        self, tmp_path, single_chromosome_fasta, expected_csv_with_ngn_pam_legacy
    ):
        """Test that we can run the script with NGN PAM"""
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(single_chromosome_fasta)
        outfile = d / "test.csv"
        gather.gather(
            inputfile=infile,
            outputfile=outfile,
            pam="NGN",
            verbose=False,
            legacy_mode=True,
        )
        assert outfile.read_text() == expected_csv_with_ngn_pam_legacy

    def test_with_ngn_pam_non_legacy(
        self, tmp_path, single_chromosome_fasta, expected_csv_with_ngn_pam_non_legacy
    ):
        """Test that we can run the script with NGN PAM"""
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(single_chromosome_fasta)
        outfile = d / "test.csv"
        gather.gather(
            inputfile=infile,
            outputfile=outfile,
            pam="NGN",
            verbose=False,
            legacy_mode=False,
        )
        assert outfile.read_text() == expected_csv_with_ngn_pam_non_legacy

    def test_with_multiple_chromosomes_legacy(
        self,
        tmp_path,
        multiple_chromasomes_fasta,
        expected_csv_with_multiple_chromosomes_legacy,
    ):
        """Test that we can run the script with multiple chromosomes"""
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(multiple_chromasomes_fasta)
        outfile = d / "test.csv"
        gather.gather(
            inputfile=infile,
            outputfile=outfile,
            pam="NGG",
            verbose=False,
            legacy_mode=True,
        )
        assert outfile.read_text() == expected_csv_with_multiple_chromosomes_legacy

    def test_with_multiple_chromosomes_non_legacy(
        self,
        tmp_path,
        multiple_chromasomes_fasta,
        expected_csv_with_multiple_chromosomes_non_legacy,
    ):
        """Test that we can run the script with multiple chromosomes"""
        d = tmp_path / "test"
        d.mkdir()
        infile = d / "test.fasta"
        infile.write_text(multiple_chromasomes_fasta)
        outfile = d / "test.csv"
        gather.gather(
            inputfile=infile,
            outputfile=outfile,
            pam="NGG",
            verbose=False,
            legacy_mode=False,
        )
        assert outfile.read_text() == expected_csv_with_multiple_chromosomes_non_legacy
