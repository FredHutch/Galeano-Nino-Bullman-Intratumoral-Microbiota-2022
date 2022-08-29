#!/usr/bin/env python3

# what we want to know:
#    1. sample name
#    2. genera list
#    2.5 number of this type of cells
#    3. UMI for each genus for this sample
#    4. read number for each genus for this sample
# First, for target sample, extract the Bacteria Positive cells
# Then using Validate csv, extract and count UMIs
# Then use CellsMeta file, count reads

def extract_bac_pos_cells(metadata_file, orig_ident):
    print(orig_ident)
    cell_names_set = set()
    metadata = open(metadata_file,'r')
    n=0
    for each_line in metadata:
        each_line = each_line.rstrip('\n')
        each_line_list = each_line.split(',')
        sample_name = each_line_list[0]
        #print (each_line_list[-4])
        if n == 0:
            k=0
            for each_item in each_line_list:
                if each_item == "Total":
                    position = k
                k+=1
        if n > 0 :
            if orig_ident in sample_name:
                if int(each_line_list[position]) > 0:
                    cell_names = each_line_list[0].split('_')[-1]
                    cell_names_set.add(cell_names)
        n+=1
    #print(len(cell_names_set))
    return cell_names_set

# validate_dict is the dict for cell_UMI -> genus
def extract_UMI(validate_file, cell_names_set):
    #print(cell_names_set)
    validate_dict = {}
    genus_set = set()
    validate = open(validate_file,'r')
    cell_name_set = set()
    for each_line in validate:
        each_line = each_line.rstrip('\n')
        cell_name = each_line.split('+')[0]
        cell_name_set.add(cell_name)
        cell_name_barcode = each_line.split(',')[0]
        #print(cell_name_barcode)
        genus = each_line.split(',')[1]
        if cell_name in cell_names_set:
            validate_dict[cell_name_barcode] = genus
            genus_set.add(genus)
    #print(cell_name_set)
    return validate_dict,genus_set

# sum dict is the dict for cell_UMI -> list of readnames
def count_read(cellsmeta_file,validate_dict):
    cellsmeta = open(cellsmeta_file,'r')
    sum_dict = {}
    for each_line in cellsmeta:
        each_line = each_line.rstrip('\n')
        each_line_list = each_line.split('\t')
        if not ',' in each_line_list[-1]:
            read_name = each_line_list[0]
            cell_name = each_line_list[1]
            barcode = each_line_list[2]
            cell_barcode = cell_name + '+' + barcode
            if cell_barcode in validate_dict:
                if not cell_barcode in sum_dict:
                    sum_dict[cell_barcode] = []
                    sum_dict[cell_barcode].append(read_name)
                else:
                    sum_dict[cell_barcode].append(read_name)
    for each_cell_barcode in sum_dict:
        sum_dict[each_cell_barcode] = list(set(sum_dict[each_cell_barcode]))
    return sum_dict

# first, loop the genus names within each sample
# for each genus names, extract and count cell_UMI, cell
# for each extracted cell_UMI, count number of *unique readnames, add together
# will be in a dict: genus[number of cell, number of UMI, number of reads]
# 
# validate_dict is the dict for cell_UMI -> genus
# sum dict is the dict for cell_UMI -> readnames
def summarize_read(sum_dict,validate_dict,genus_set):
    genus_sum_dict = {}
    for each_genus in genus_set:
        for each_cell_UMI in validate_dict:
            if validate_dict[each_cell_UMI] == each_genus:
                cell_barcode = each_cell_UMI.split('+')[0]
                #print(cell_barcode)
                #print(each_cell_UMI)
                read_list = sum_dict[each_cell_UMI]
                if not each_genus in genus_sum_dict:
                    genus_sum_dict[each_genus] = {}
                    genus_sum_dict[each_genus]['cell_list']=[]
                    genus_sum_dict[each_genus]['UMI_list']=[]
                    genus_sum_dict[each_genus]['reads_list']=[]
                genus_sum_dict[each_genus]['cell_list'].append(cell_barcode)
                genus_sum_dict[each_genus]['UMI_list'].append(each_cell_UMI)
                genus_sum_dict[each_genus]['reads_list'] = genus_sum_dict[each_genus]['reads_list'] + read_list 
    # then convert it to count dict
    return genus_sum_dict#genus_count_dict

def add_dicts(genus_sum_dict_1,genus_sum_dict_2):
    genus_sum_dict1 = genus_sum_dict_1
    genus_sum_dict2 = genus_sum_dict_2
    for each_genus in genus_sum_dict2:
        if each_genus in genus_sum_dict1:
            genus_sum_dict1[each_genus]['cell_list'] += genus_sum_dict2[each_genus]['cell_list']
            genus_sum_dict1[each_genus]['UMI_list'] += genus_sum_dict2[each_genus]['UMI_list']
            genus_sum_dict1[each_genus]['reads_list'] += genus_sum_dict2[each_genus]['reads_list']
        else:
            genus_sum_dict1[each_genus] = {}
            genus_sum_dict1[each_genus]['cell_list'] = genus_sum_dict2[each_genus]['cell_list']
            genus_sum_dict1[each_genus]['UMI_list'] = genus_sum_dict2[each_genus]['UMI_list']
            genus_sum_dict1[each_genus]['reads_list'] = genus_sum_dict2[each_genus]['reads_list']
    genus_sum_dict = genus_sum_dict1
    # then convert it to count dict
    genus_count_dict = {}
    for each_genus in genus_sum_dict:
        #print(genus_sum_dict[each_genus])
        number_of_cells = len(set(genus_sum_dict[each_genus]['cell_list']))
        number_of_UMIs = len(set(genus_sum_dict[each_genus]['UMI_list']))
        number_of_reads = len(set(genus_sum_dict[each_genus]['reads_list']))
        if not each_genus in genus_count_dict:
            genus_count_dict[each_genus] = {}
            genus_count_dict[each_genus]['cell'] = 0
            genus_count_dict[each_genus]['UMI'] = 0
            genus_count_dict[each_genus]['reads'] = 0
        genus_count_dict[each_genus]['cell'] = number_of_cells
        genus_count_dict[each_genus]['UMI'] = number_of_UMIs
        genus_count_dict[each_genus]['reads'] = number_of_reads
    return genus_count_dict

def output_read(output_file_name, genus_count_dict):
    output_file = open(output_file_name,'w')
    header = 'Genus,Number_of_Cells,Number_of_UMI,Number_of_reads\n'
    output_file.write(header)
    for each_genus in genus_count_dict:
        number_of_cells = genus_count_dict[each_genus]['cell'] 
        number_of_UMIs = genus_count_dict[each_genus]['UMI'] 
        number_of_reads = genus_count_dict[each_genus]['reads']
        output_line = each_genus + ',' + str(number_of_cells) + ',' + str(number_of_UMIs) + ',' + str(number_of_reads) + '\n'
        output_file.write(output_line)
    return

metadata_file = '/processing/patient_sample/validate/metadata.csv'

mi_folder = '/processing/patient_sample/miseq/python/'
nova_folder = '/processing/patient_sample/novaseq/python/'

sample_name_list = [
    '9218',
    '9236',
    '9237',
    '9347',
    '9398',
    'BM319435',
    'BM320030'
]

nova_pattern='.nova.'
mi_pattern='.mi.'
validate_csv_pattern='filtered_matrix.validate.csv'
readnamepath_pattern='raw.filtered_matrix.readnamepath'
for each_sample in sample_name_list:
    orig_ident = each_sample
    cell_names_set = extract_bac_pos_cells(metadata_file, orig_ident)

    nova_validate_csv = nova_folder+each_sample+nova_pattern+validate_csv_pattern
    validate_dict,genus_set = extract_UMI(nova_validate_csv, cell_names_set)
    nova_readnamepath_csv = nova_folder+each_sample+nova_pattern+readnamepath_pattern
    sum_dict = count_read(nova_readnamepath_csv,validate_dict)
    genus_count_dict_nova = summarize_read(sum_dict,validate_dict,genus_set)

    mi_validate_csv = mi_folder+each_sample+mi_pattern+validate_csv_pattern
    validate_dict,genus_set = extract_UMI(mi_validate_csv, cell_names_set)
    mi_readnamepath_csv = mi_folder+each_sample+mi_pattern+readnamepath_pattern
    sum_dict = count_read(mi_readnamepath_csv,validate_dict)
    genus_count_dict_mi = summarize_read(sum_dict,validate_dict,genus_set)

    output_file = '/processing/patient_sample/validate/'+each_sample+'.mi.sum.csv'

    output_file = '/processing/patient_sample/validate/'+each_sample+'.nova.sum.csv'

    genus_count_dict = add_dicts(genus_count_dict_nova,genus_count_dict_mi)
    output_file = '/processing/patient_sample/validate/'+each_sample+'.sum.csv'
    output_read(output_file, genus_count_dict)

