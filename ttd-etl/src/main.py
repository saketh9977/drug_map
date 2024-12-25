import json
import re

def parse_biomarker_disease_map_file(biomarker_disease_filepath):
    """
        assumption:
            file starts with actual data, no metadata -

            BM003549	Neutrophil gelatinase-associated lipocalin (LCN2)	Smallpox	ICD-11: 1E70	ICD-10: B03	.
            BM002188	Monocyte chemoattractantprotein-1 (MCP-1)	Amyotrophic lateral sclerosis	ICD-11: 8B60.0	.	ICD-9: 335.2
            BM001695	HLA class I histocompatibility antigen, B-8 alpha chain (HLA-B)	Myasthenia gravis	ICD-11: 8C6Y	ICD-10: G70.0	ICD-9: 358
    """

    with open(biomarker_disease_filepath, 'r') as in_stream:
        out = []
        for line in in_stream:

            line = line.strip()
            if line == '':
                continue
            token_list = line.split('\t')

            icd11 = ' '.join(token_list[-3].split(' ')[1:])
            icd10 = ' '.join(token_list[-2].split(' ')[1:])
            icd9 = ' '.join(token_list[-1].split(' ')[1:])

            cur_dict = {
                'ttd_biomarker_id': token_list[0],
                'ttd_biomarker_name': token_list[1],
                'ttd_disease_name': token_list[2],
                'icd11': icd11,
                'icd10': icd10,
                'icd9': icd9,
            }

            # handle empty values
            for key in cur_dict:
                if cur_dict[key] == '.':
                    cur_dict[key] = ''
            # --------------------------------------

            out.append(cur_dict)

        return out

def parse_drug_synonyms_file(drug_synonyms_filepath):
    """
        assumption: 
            file starts with actual data, no metadata -

            D00AAN	TTDDRUID	D00AAN
            D00AAN	DRUGNAME	8-O-(4-chlorobenzenesulfonyl)manzamine F
            D00AAN	SYNONYMS	CHEMBL400717

            D00AAU	TTDDRUID	D00AAU
            D00AAU	DRUGNAME	3-[1-ethyl-2-(3-hydroxyphenyl)butyl]phenol
            D00AAU	SYNONYMS	Metahexes trol
    """

    with open(drug_synonyms_filepath, 'r') as in_stream:
        cur_mapping = {}
        out = []
        for line in in_stream:

            line = line.strip()

            # handle new line
            if line == '':
                if len(cur_mapping) != 0:
                    out.append(cur_mapping)
                cur_mapping = {}
                continue
            # ---------------------------------------------------------

            # split line
            token_list = line.split('\t')
            prop_name = token_list[1]
            prop_val = token_list[-1]
            # ---------------------------------------------------------

            if prop_name == 'TTDDRUID':
                cur_mapping['ttd_drug_id'] = prop_val
            elif prop_name == 'DRUGNAME':
                cur_mapping['ttd_drug_name'] = prop_val
            elif prop_name == 'SYNONYMS':
                
                if cur_mapping.get('ttd_drug_synonym') is None:
                    cur_mapping['ttd_drug_synonym'] = []

                cur_mapping['ttd_drug_synonym'].append(prop_val)
        
        # handle last mapping
        if len(cur_mapping) != 0:
            out.append(cur_mapping)
        # ---------------------------------------------------------

    return out

def parse_drug_disease_map_file(drug_disease_map_filepath):

    """
        assumption:
            file starts with actual data, no metadata -

            TTDDRUID	DZB84T		
            DRUGNAME	Maralixibat		
            INDICATI	Pruritus	ICD-11: EC90	Approved
            INDICATI	Progressive familial intrahepatic cholestasis	ICD-11: 5C58.03	Phase 3
            INDICATI	Alagille syndrome	ICD-11: LB20.0Y	Phase 2

            TTDDRUID	DZA90G		
            DRUGNAME	BNT162b2		
            INDICATI	Coronavirus Disease 2019 (COVID-19)	ICD-11: 1D6Y	Approved

            TTDDRUID	DZ8DF0		
            DRUGNAME	Nedosiran		
            INDICATI	Primary hyperoxaluria type 1	ICD-11: 5C51.20	Approved
            INDICATI	Hyperoxaluria	ICD-11: 5C51.2	Phase 2

    """
    
    with open(drug_disease_map_filepath, 'r') as in_stream:
        cur_mapping = {}
        out = []
        for line in in_stream:
            
            line = line.strip()

            # handle new line
            if line == '':
                if len(cur_mapping) != 0:
                    out.append(cur_mapping)
                cur_mapping = {}
                continue
            # ---------------------------------------------------------

            # split line
            token_list = line.split('\t')
            prop_name = token_list[0]
            prop_val = '\t'.join(token_list[1:])
            # ---------------------------------------------------------

            if prop_name == 'TTDDRUID':
                cur_mapping['ttd_drug_id'] = prop_val
            elif prop_name == 'DRUGNAME':
                cur_mapping['ttd_drug_name'] = prop_val
            elif prop_name == 'INDICATI':
                
                if cur_mapping.get('ttd_indication') is None:
                    cur_mapping['ttd_indication'] = []
                
                indication_tokens = prop_val.split('\t')

                # handle icd codes
                icd_tokens = indication_tokens[1].split(' ')
                if icd_tokens[0] == 'ICD-11:':
                    icd_prop_name = 'icd11'
                else:
                    icd_prop_name = re.sub(r"[:\-]", "", icd_tokens[0]).lower()

                icd_prop_val = ' '.join(icd_tokens[1:])
                if icd_prop_val.lower() == 'n.a.':
                    icd_prop_val = ''
                # ---------------------------------------------------------

                cur_mapping['ttd_indication'].append({
                    'name': indication_tokens[0],
                    icd_prop_name: icd_prop_val,
                    'clinical_status': indication_tokens[-1]
                })

        # handle last mapping
        if len(cur_mapping) != 0:
            out.append(cur_mapping)
        # ---------------------------------------------------------

    return out

def main():

    drug_disease_map_filepath = '../data/P1-05-Drug_disease.txt'
    parsed_drug_disease_map = parse_drug_disease_map_file(drug_disease_map_filepath)
    with open('../out/drug_disease.json', 'w+') as out_stream:
        json.dump(parsed_drug_disease_map, out_stream, indent=4)

    drug_synonym_filepath = '../data/P1-04-Drug_synonyms.txt'
    parsed_drug_synonyms = parse_drug_synonyms_file(drug_synonym_filepath)
    with open('../out/drug_synonym.json', 'w+') as out_stream:
        json.dump(parsed_drug_synonyms, out_stream, indent=4)

    biomarker_disease_map_filepath = '../data/P1-08-Biomarker_disease.txt'
    parsed_biomarker_disease_map = parse_biomarker_disease_map_file(biomarker_disease_map_filepath)
    with open('../out/biomarker_disease.json', 'w+') as out_stream:
        json.dump(parsed_biomarker_disease_map, out_stream, indent=4)

if __name__ == '__main__':
    main()
