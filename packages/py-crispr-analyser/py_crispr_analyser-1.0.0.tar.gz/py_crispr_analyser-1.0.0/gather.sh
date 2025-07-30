#!/bin/bash

for file in ../cansu_work/fasta/Homo_sapiens.GRCh38.dna.chromosome.*.fa; do
  FILE_NAME=$(basename "$file")
  CHROMOSOME=`echo $FILE_NAME | sed "s/Homo_sapiens\.GRCh38.dna.chromosome\.\(.*\)\.fa/\1/"`
  
  poetry run gather -i $file -o "csv/c$CHROMOSOME.csv" -p NGN
done
