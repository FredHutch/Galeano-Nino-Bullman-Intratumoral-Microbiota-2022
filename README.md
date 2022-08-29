# Galeano-Nino-Bullman-Intratumoral-Microbiota-2022

Analysis code used in Galeano Nino, et al. 2022

The code in this repository is organized to reflect the description in the Methods
section of Galeano Nino, et al. 2022.

# Overview of Computational Pipeline for INVADEseq
## Part 1: Single cell data
###   Preprocess:
    1. Identification of microbial reads within single cells GEX libraries (Pipeline_GEX.sh)
    2. INVADEseq bacterial 16S rRNA gene libraries (Pipeline_16S.sh)
    3. Combine and deduplication of microbial metadata from step 1 & 2 ( merge_metadata.py and metadata_dedup.py)
###   Processing of single cell data
    1. Seurat data processing, Harmony integration, SingleR annotation and CopyKAT predication (Single_Cell.r)
    2. Differentially expression analysis and GSEA (DE.r)
    3. summarize number of bacteria reads and UMIs in single cell data (validate_and_count.py)
## Part 2: Visium data
    1. Identification of microbial reads within 10x Visium spatial transcriptomic data (Pipeline_Visium.sh)
    2. Bioinformatic analysis of 10x Visium spatial transcriptomic data (Visium.r)

