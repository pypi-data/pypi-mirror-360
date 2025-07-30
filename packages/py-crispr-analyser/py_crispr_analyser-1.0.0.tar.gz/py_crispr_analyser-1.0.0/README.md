# Python CRISPR Analyser

The Python CRISPR Analyser is a set of libraries and scripts that allows you to index [CRISPR](https://en.wikipedia.org/wiki/CRISPR)s from FASTA genome files and use the resulting index to find CRISPRS by using guide RNA (gRNA) sequences and to find off-targets for a given gRNA sequence.

## About

This tool is a re-write of the original [CRISPR Analyser](https://github.com/htgt/CRISPR-Analyser) written in C++ with the intention that the Python version will be easier to use and extend.
The following workflow is supported:
- **Gathering** CRISPRs from a FASTA file specifying the PAM sequence and the length of the gRNA,
- **Indexing** the CRISPRs into a binary formatted index for fast search,
- **Searching** for CRISPRs by using a gRNA sequence,
- **Aligning** the gRNA sequence to the CRISPRs to find off-targets.

Furthermore library functions can be used directly in a users own code to perform the above tasks.

## Prerequisites

The Python CRISPR Analyser requires Python 3.12 or later. If using the database functionality you should have SQLite3 installed. If using CUDA, you will need to have a compatible Nvidia GPU and the CUDA kernel drivers installed, we have testing with CUDA 12.4.

## Installation

To install the Python CRISPR Analyser:

The easiest approach is to install using Pip

```bash
pip install <TODO>
pip install -i https://pypi.org/simple/py-crispr-analyser
```

The source code can be downloaded from Github:
<TODO> check this

```bash
git clone git@github.com:htgt/py-crispr-analyser.git
```

Make sure you have Python 3.12 or later.

## Usage

Python CRISPR Analyser is intended to be installed as a library.

### Gather

To run the **Gather** command:

```bash
crispr_analyser_gather -i <input_fasta> -o <output_file> -p <pam_sequence>
```

The parameters are:
- *-i*, *--ifile* - the Input File needs to be a FASTA file containing the genenome sequence. For example GRCh38 which can be downloaded from [Ensembl](https://ftp.ensembl.org/pub/release-113/fasta/homo_sapiens/dna/) - *Required*,
- *-o*, *--ofile* - the Output File which will be a CSV file (without headers) - *Required*,
- *-p*, *--pam* - the PAM sequence which can consist of A, C, G, T and N (for any) - *Required*,
- *-h*, *--help* - shows the help

For example:

```bash
crispr_analyser_gather -i Homo_sapiens.GRCh38.dna.chromosome.18.fa -o chromosome.18.csv -p "NGG"
```

### Index

To run the **Index** command:

```bash
crispr_analyser_index -i <input_csv> -a <assembly> -o <offset> -o <output_bin> -s <species> -e <species_id> -g <guide_length> -p <pam_length>
```

The parameters are:
- *-i*, *--ifile* - The Input CSV file, can be declared one or many times (see example below) - *Required*,
- *-o*, *--ofile* - The Output binary file - *Required*,
- *-a*, *--assembly* - The name of the genome assembly - *Required*,
- *-s*, *--species* - The name of the species - *Required*,
- *-f*, *--offset* - the offset after which to start the ID for CRISPRS, defaults to 0,
- *-e*, *--species_id* - The species ID, defaults to 0,
- *-g*, *--guide_length* - The length of the gRNA, defaults to 20,
- *-p*, *--pam_length* - The length of the PAM, defaults to 3,
- *-h*, *--help* - shows the help

for example:

```bash
crispr_analyser_index -i chromosome.1.csv -i chromosome.2.csv -o guides.bin -a GRCh38 -s Human
```

The CSV input file must have the following fields:
- Chromasome Name as a string e.g. '18'
- Position Start - an integer indicating the start position offset from the start of the Chromasome (using 5' to 3' orientation),
- CRISPR Sequence - the string representing the CRISPR including the PAM,
- PAM Right? - a 1 or 0 (true or false) indicating if the PAM is on the right side of the CRISPR,
- Species ID - this is currently always set to 1.

Note that *Species ID* is a legacy field and is not used in the current version of the software.

### Find CRISPR IDs given a gRNA sequence

Run the **Search** command as follows:

```bash
crispr_analyser_search -i <input_bin> -s <gRNA_sequence>
```

The parameters are:
- -i, --ifile - The Input binary guides file - *Required*,
- -s, --search - The gRNA sequence - *Required*.

Output is split between STDERR and STDOUT. The IDs of the CRISPRs are printed to STDOUT and the summary of the search is printed to STDERR.

For example, output to STDERR might look like:

```bash
Version is 3
Assembly is GRCh38 (Human)
File has 1200559014 sequences
Sequence length is 20
Offset is 0
Species id is 1
Loading took 12.25 seconds
Loaded 1200559014 sequences
Found 1 exact matches
Found the following matches:
```

And the CRISPR IDS found would be printed to STDOUT, separated by newlines:

```bash
1200551676
3249821234
```

### Find off-targets for given CRISPR IDs

We can calculate the summary of off-targets for one or more CRISPRs given their ID and using the **Align** command as follows:

```bash
crispr_analyser_align -i <input_bin> [ids]
```

The parameters are:
- -i, --ifile - The Input binary guides file - *Required*
- --no-cuda - Disable CUDA GPU acceleration
- [ids] - one or more IDs of the CRISPRs to search for off-targets - *Required*

As with the **Search** command, the output is split between STDERR and STDOUT. The summary of the search is printed to STDERR and the off-targets are printed to STDOUT.

For example, output to STDERR might look like:

```bash
Assembly is GRCh38 (Human)
File has 1200559014 sequences
Sequence length is 20
Offset is 0
Species id is 1
Loading took 7.33 seconds
```

And the off-targets found would be printed to STDOUT, separated by newlines. The format for off-targets for each CRISPR ID is:

```bash
<CRISPR ID> <Species ID> <Off-Target CRISPR IDS> <Summary>
```

For example:

```bash
1200551673	1	{5631600,12587091,19109163,22079030,23239000,26501597,30414111,33581723,34229111,34705555,37873467,43668607,45229014,50360433,51303777,53203244,53787722,54810107,55678064,56111581,57172117,60111258,65696513,73938350,78186291,78909324,79032225,79131485,79199752,81814531,83282318,89311432,91700045,94095775,104106532,110628740,117838121,119302948,120328606,121417854,123785758,128025190,129308028,129383427,131704114,141154489,143221468,144953871,153584006,156820656,159690561,162463025,165704925,166653098,169556513,169894014,170813225,172596043,173336999,176798557,176900263,179624805,179879820,180325270,183714994,183725616,187191479,188483145,190105865,194567945,195833213,199102585,199290226,204836295,205765766,213995462,215497592,217290825,218224164,218365574,219065926,222205282,228956564,230872099,231530511,233998802,235057869,236017990,242874656,252500366,252748162,261804881,269244299,270042584,272049195,277367575,280089801,284873674,285627010,287098376,288534000,289237233,289343988,289586896,290746480,298407995,299035379,299567888,305616511,308195124,309038582,313972681,314572210,314878175,316358683,316911638,323421292,325962990,326919721,329949795,331922709,334295731,334846296,338562318,341435450,341728613,342597884,343360904,343429153,352681255,353840365,357616747,357754197,358166591,368932159,379035147,380305864,385343331,388328199,392759812,394013711,395936214,408491849,408755686,410174279,414936251,418511742,425649740,427086025,427886947,429883343,435641334,436616343,437452167,441768519,442845158,444661399,444882063,445672975,447255070,464745129,470350960,471383043,473890728,475060642,475095613,476200278,477156460,479489876,490092071,493128577,500044319,503670391,504239932,506502770,511566658,513551025,515010796,516910537,518522314,518874302,527066517,532871367,540555229,545417977,546590944,548995953,554798163,560390395,561444072,562793216,567065284,570069112,571278043,572715670,575189618,578564090,583318535,590254469,595390813,598450204,599871415,600025117,602055868,602803144,604432573,606497148,607805800,609515434,612971857,613980801,614891455,616693924,617497175,618674279,618693888,619233704,620102197,620871357,627733346,643459607,647558077,650210205,654411215,656081271,656174099,657016785,659425058,662332362,666877185,668392011,670105960,671623434,673828082,676419287,678522049,680269126,681812795,682181056,683858037,687904397,688086499,695096280,699808758,700377621,708176275,714939183,724429779,727287866,730342818,734284179,746863119,756989553,764145480,769124497,772312880,772734053,772994362,776138952,778124819,787329528,794112125,801591361,803539013,807757046,810087625,811896473,824317786,827097789,828717444,833506447,835651412,841880152,844083167,845039322,847014004,849545231,851108109,851287298,855567341,856446172,863783477,864162969,873077012,878677577,882676574,884021802,904384677,906818273,908646372,914503814,919559357,922317697,922699712,923562980,923905133,926409128,929053437,929419673,929656450,935525941,948268750,949547398,949827174,950751939,954122925,957141360,964414988,964488502,965562242,968418491,973758282,974537517,978780419,981858792,998620175,1000284084,1006076964,1012073812,1014825674,1016416691,1020485961,1020497125,1022107423,1023413695,1027567634,1030193706,1030733180,1031536226,1034216041,1037422056,1044851271,1048162796,1052896575,1054970838,1060958364,1061603994,1064490807,1065149388,1065786298,1070371661,1072182346,1072279792,1081522519,1082356418,1083654553,1083959717,1087957969,1094427998,1096775589,1099668608,1107229436,1108523358,1113194026,1118220025,1134507117,1135049225,1135867617,1139813789,1142353946,1144755203,1146013879,1147253218,1153982157,1164707102,1165778714,1167191051,1167628030,1170541198,1173456426,1173689054,1176790664,1178223456,1181252406,1200551673}	{0: 1, 1: 0, 2: 4, 3: 18, 4: 352}
910190339	1	{0: 1, 1: 7, 2: 109, 3: 951, 4: 2452}
```

Note that any CRISPRs with more than 2000 off-targets will not have the off-target CRISPR IDs printer to STDOUT as shown in the second CRISPR above.

### GPU Acceleration

The **Align** command will run on GPUs if it detects a compatible Nvidia GPU. Note that CUDA libraries are only installed on Linux. To disable GPU acceleration use the *--no-cuda* flag. This software supports CUDA 12 but depending on the minor version of CUDA you may need to run the **Align** command with the *NUMBA_CUDA_ENABLE_PYNVJITLINK=1* environmental variable. For example:

```bash
NUMBA_CUDA_ENABLE_PYNVJITLINK=1 crispr_analyser_align -i grch38_ngg.bin 23322 44343
```

## Cross Referencing Guides to CRISPRs

The *Index* stage of the pipeline will create a binary file containing the gRNA guides. In order to cross reference the guides to the CRISPRs found in the *Gather* stage it is recommended to use a database as *Search* and *Align* will only give a CRISPR ID.
For most applications this will be a SQLite database (as it is read-only) but other databases can be used.

To set up an SQLite database, first install SQLite3 and then create a database file:

```bash
sqlite3 crispr.db
```

we will use a table to hold the CRISPRs data as follows:

```sql
CREATE TABLE crisprs (
    id integer primary key,
    chr_name text,
    chr_start integer,
    seq text,
    pam_right integer,
);
```

We include a script to automate this for you using SQLite3:

```bash
python scripts/index_database.py -d crispr.db \
  -i chromosome.1.csv \
  -i chromosome.2.csv \
  -i chromosome.3.csv \
  ...
```

Note that the offset is set to 0 by default, if you have set a different offset in the *Index* stage then you will need to set the offset with the *-o* flag.

Also note that the sequence with which the *-i* flag is used determines the order of the importation of the CRISPRs into the database.

## Testing

Make sure you have installed the source code and. Pytest need to be installed, this can be done using pip to install the development tools (which includes black, flake8 and pytest):

```bash
pip install '.[dev]'
```

To run the unit tests:

```bash
pytest tests
```

## Copyright

Copyright (C) 2025 Genome Research Ltd.

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

[Cellular Informatics Team](https://www.sanger.ac.uk/group/cellular-informatics/) at the [Wellcome Sanger Institute](https://www.sanger.ac.uk/), Hinxton, UK - [wge@sanger.ac.uk](mailto:wge@sanger.ac.uk)
