# Galeano-Nino-Bullman-Intratumoral-Microbiota-2022

Analysis code used in Galeano Nino, et al. 2022

The code in this repository is organized to reflect the description in the Methods
section of Galeano Nino, et al. 2022.

# Overview of Computational Pipeline for INVADEseq
## part 1: Single cell data
##   Preprocess:
###   1. Identification of microbial reads within single cells GEX libraries (Pipeline_GEX.sh)
###   2. INVADEseq bacterial 16S rRNA gene libraries (Pipeline_16S.sh)
###   3. Combine and deduplication of microbial metadata from step 1 & 2 ( merge_metadata.py and metadata_dedup.py)
##   Processing of single cell data
###   1. (Single_Cell.r)
###   2. (DE.r)

## part 2: Visium data

##   Preprocess:
###   1. 
