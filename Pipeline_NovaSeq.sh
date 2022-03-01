#!/bin/bash
ml GATK/4.1.3.0-GCCcore-8.3.0-Java-1.8
ml Python
ml Krona/2.7.1-GCCcore-9.3.0-Perl-5.30.2
# load GATK/Pytho/Krona packages, required packages also available through Anaconda
# ROOT is the output directory
root=ROOT
# CELLRANGER_FOLDER containing cellranger count output folders, named by sample names
bam_path=CELLRANGER_FOLDER
# Pathseq database directory
pathseqdb=PATHSEQDB

cd ${bam_path}
outpath=${root}
mkdir ${outpath}
outpath=${outpath}/pathseq
mkdir ${outpath}
for folder in *
do
folder_name=${folder##*/}
file=${folder}/outs/possorted_genome_bam.bam
samplename=${folder_name}
echo ${samplename}
gatk --java-options "-Xmx750g" PathSeqPipelineSpark \
    --input ${file} \
    --filter-bwa-image ${pathseqdb}/pathseq_host.fa.img \
    --kmer-file ${pathseqdb}/pathseq_host.bfi \
    --min-clipped-read-length 60 \
    --microbe-fasta ${pathseqdb}/pathseq_microbe.fa \
    --microbe-bwa-image ${pathseqdb}/pathseq_microbe.fa.img \
    --taxonomy-file ${pathseqdb}/pathseq_taxonomy.db \
    --output ${outpath}/${samplename}.pathseq.complete.bam \
    --scores-output ${outpath}/${samplename}.pathseq.complete.csv \
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

ml Python
ml Pysam
pathseq_path=${root}/pathseq
out_path=${root}/python
mkdir ${out_path}
cd ${bam_path}
# with updated python (validate files included)
for each_sample in *
do
echo ${each_sample}
python UMI_annotator.py \
${bam_path}/${each_sample}/outs/possorted_genome_bam.bam \
Sample_${each_sample} \
${bam_path}/${each_sample}/outs/filtered_feature_bc_matrix/barcodes.tsv.gz \
${pathseq_path}/${each_sample}.pathseq.complete.bam \
${pathseq_path}/${each_sample}.pathseq.complete.csv \
${out_path}/${each_sample}.nova.filtered_matrix.readname \
${out_path}/${each_sample}.nova.filtered_matrix.unmap_cbub.bam \
${out_path}/${each_sample}.nova.filtered_matrix.unmap_cbub.fasta \
${out_path}/${each_sample}.nova.filtered_matrix.list \
${out_path}/${each_sample}.nova.raw.filtered_matrix.readnamepath \
${out_path}/${each_sample}.nova.filtered_matrix.genus.cell \
${out_path}/${each_sample}.nova.filtered_matrix.genus.csv \
${out_path}/${each_sample}.nova.filtered_matrix.validate.csv
done

