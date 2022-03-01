#!/bin/bash
ml Trimmomatic/0.39-Java-11
ml BEDTools/2.29.2-GCC-9.3.0
ml SAMtools/1.10-GCCcore-8.3.0
ml FastQC/0.11.9-Java-11
ml picard/2.21.6-Java-11
ml Python
ml Krona/2.7.1-GCCcore-9.3.0-Perl-5.30.2
ml Pysam
# ROOT is the output directory
root=ROOT
# CELLRANGER_FOLDER containing MiSeq cellranger count output folders, named by sample names
raw_data_folder=CELLRANGER_FOLDER
# CELLRANGER_FOLDER_NOVA containing NovaSeq cellranger count output folders (not MiSeq), named by sample names
nova_bam_path=CELLRANGER_FOLDER_NOVA
# Pathseq database directory
pathseqdb=PATHSEQDB

workdir=${root}
cd ${workdir}

mkdir split_reads
cd split_reads
for folder in ${raw_data_folder}/*
do
folder_name=${folder##*/}
file=${folder}/outs/possorted_genome_bam.bam
echo ${file}
samplename=${folder_name}
folder_name=${folder##*/}
file=${folder}/outs/possorted_genome_bam.bam
samplename=${folder_name}
bedtools bamtofastq -i ${file} \
                      -fq ${samplename}.r1.fq \
                      -fq2 ${samplename}.r2.fq
done

mkdir ${root}/preqc
fastqc \
-o ${root}/preqc \
-t 36 \
${root}/split_reads/*.fq

cd ${root}/split_reads
mkdir trim
for str in *r1.fq
do
java -jar $EBROOTTRIMMOMATIC/trimmomatic-0.39.jar SE \
-threads 36 \
${str} \
trim/${str}.SE_trim.fq \
ILLUMINACLIP:$EBROOTTRIMMOMATIC/adapters/TruSeq3-PE-2.fa:2:30:10 \
LEADING:3 TRAILING:3 SLIDINGWINDOW:4:15 MINLEN:36 HEADCROP:15
done

cd trim
mkdir ${root}/postqc
fastqc \
-o ${root}/postqc \
-t 36 *.SE_trim.fq

mkdir ${workdir}/ubams_r1
cd ${root}/split_reads/trim

for file in *SE_trim.fq
do
java -Xmx750G -jar $EBROOTPICARD/picard.jar FastqToSam \
    FASTQ=${file} \
    OUTPUT=${file}.bam \
    READ_GROUP_NAME=H0164.2 \
    SAMPLE_NAME=PRJNA627695 \
    LIBRARY_NAME=Solexa-272222 \
    PLATFORM_UNIT=H0164ALXX140820.2 \
    PLATFORM=illumina 

mv ${file}.bam ${workdir}/ubams_r1
done

folder=${workdir}/ubams_r1
outpath=${workdir}/pathseq_r1
mkdir ${outpath}
ml GATK/4.1.3.0-GCCcore-8.3.0-Java-1.8
cd ${folder}

for each_file in *.bam
do
filename="${each_file%.*}"
filename="${filename%.*}"
filename="${filename%.*}"
samplename=$filename
echo $filename
gatk --java-options "-Xmx750g" PathSeqPipelineSpark \
    --input ${each_file} \
    --filter-bwa-image ${pathseqdb}/pathseq_host.fa.img \
    --kmer-file ${pathseqdb}/pathseq_host.bfi \
    --min-clipped-read-length 60 \
    --microbe-fasta ${pathseqdb}/pathseq_microbe.fa \
    --microbe-bwa-image ${pathseqdb}/pathseq_microbe.fa.img \
    --taxonomy-file ${pathseqdb}/pathseq_taxonomy.db \
    --output ${outpath}/${samplename}.pathseq.complete.bam \
    --scores-output ${outpath}/${samplename}.pathseq.complete.txt.csv \
    --is-host-aligned false \
    --filter-duplicates false \
    --min-score-identity .7
done

csv_dir=$outpath
cd $csv_dir
mkdir krona
for input in *.csv
do
python create_Krona_input_updated.py $csv_dir/$input
done
cd krona
for each_csv in *.krona
do
echo ${each_csv}
ImportText.pl \
${each_csv} \
-o ${each_csv}.html
done

bam_path=${raw_data_folder}
pathseq_path=${workdir}/pathseq_r1
out_path=${workdir}/python
mkdir ${out_path}
cd ${bam_path}
# with updated python (validate files included)
for each_sample in *
do
echo ${each_sample}
python python UMI_annotator.py \
${bam_path}/${each_sample}/outs/possorted_genome_bam.bam \
Sample_${each_sample} \
${nova_bam_path}/${each_sample}/outs/filtered_feature_bc_matrix/barcodes.tsv.gz \
${pathseq_path}/${each_sample}.r1.fq.pathseq.complete.bam \
${pathseq_path}/${each_sample}.r1.fq.pathseq.complete.txt.csv \
${out_path}/${each_sample}.mi.filtered_matrix.readname \
${out_path}/${each_sample}.mi.filtered_matrix.unmap_cbub.bam \
${out_path}/${each_sample}.mi.filtered_matrix.unmap_cbub.fasta \
${out_path}/${each_sample}.mi.filtered_matrix.list \
${out_path}/${each_sample}.mi.raw.filtered_matrix.readnamepath \
${out_path}/${each_sample}.mi.filtered_matrix.genus.cell \
${out_path}/${each_sample}.mi.filtered_matrix.genus.csv \
${out_path}/${each_sample}.mi.filtered_matrix.validate.csv
done

