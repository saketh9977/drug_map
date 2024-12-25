import json
import re

def parse_ttd_drug_to_external_db_map_file(ttd_drug_to_external_db_map_filepath):
    """
        assumption:
            file starts with actual data, no metadata -

            D00AEQ	TTDDRUID	D00AEQ
            D00AEQ	DRUGNAME	Hydroxyprogesterone
            D00AEQ	D_FOMULA	C21H30O3
            D00AEQ	PUBCHCID	6238
            D00AEQ	PUBCHSID	10348; 80880; 855528; 7848012; 10257140; 12209772; 15007174; 24895697; 46243005; 49834232; 53788881; 56424128; 57351759; 75144784; 81093219; 87571349; 90473603; 93576739; 103770831; 103823738; 113466682; 117622268; 124576771; 124799532; 124886752; 127764370; 131321883; 131549786; 134976956; 137124474; 143449668; 144207051; 144212650; 160843844; 162092117; 163270260; 164788675; 170465210; 174529979; 175265862; 179316277; 184545682; 198993584; 223439966; 226397056; 241113174; 250112560; 252122136; 252308498; 252401932
            D00AEQ	CASNUMBE	CAS 68-96-2
            D00AEQ	CHEBI_ID	CHEBI:17252
            D00AEQ	SUPDRATC	G03DA03

            D00AMQ	TTDDRUID	D00AMQ
            D00AMQ	DRUGNAME	Ethanol
            D00AMQ	D_FOMULA	C2H6O
            D00AMQ	PUBCHCID	702
            D00AMQ	PUBCHSID	2694; 3752; 122577; 588484; 601786; 825155; 827842; 841053; 3137603; 7344411; 7847136; 7887325; 7887328; 7889563; 7889631; 7979196; 8145680; 8150751; 10531509; 14709184; 15170309; 17389892; 24439064; 24845303; 24845391; 24845392; 24845393; 24845394; 24845395; 24845396; 24845397; 24845398; 24845399; 24845400; 24845401; 24845402; 24845403; 24845404; 24845405; 24845406; 24845407; 24845408; 24851272; 24854453; 24854455; 24854458; 24854460; 24854502; 24854733; 24856395
            D00AMQ	CASNUMBE	CAS 64-17-5
            D00AMQ	CHEBI_ID	CHEBI:16236
            D00AMQ	SUPDRATC	D08AX08; V03AB16; V03AZ01
            D00AMQ	SUPDRCAS	cas=000051412

            D00AOJ	TTDDRUID	D00AOJ
    """

    with open(ttd_drug_to_external_db_map_filepath, 'r') as in_stream:
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
            # -----------------------------------

            # split line
            token_list = line.split('\t')
            prop_name = token_list[1]
            prop_val = token_list[2]
            # -----------------------------------

            if prop_name == 'TTDDRUID':
                cur_mapping['ttd_drug_id'] = prop_val
            elif prop_name == 'DRUGNAME':
                cur_mapping['ttd_drug_name'] = prop_val
            elif prop_name == 'D_FOMULA':
                cur_mapping['drug_chemical_formula'] = prop_val
            elif prop_name == 'PUBCHCID':
                cur_mapping['drug_pubchem_cid'] = prop_val
            elif prop_name == 'PUBCHSID':
                cur_mapping['drug_pubchem_sid'] = prop_val
            elif prop_name == 'CASNUMBE':
                cur_mapping['drug_cas_number'] = prop_val
            elif prop_name == 'CHEBI_ID':
                cur_mapping['drug_chebi_id'] = prop_val
            elif prop_name == 'SUPDRATC':
                cur_mapping['drug_superdrug_atc'] = prop_val
            elif prop_name == 'SUPDRCAS':
                cur_mapping['drug_superdrug_cas'] = prop_val

        # handle last mapping
        if len(cur_mapping) != 0:
            out.append(cur_mapping)

    return out


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

    ttd_drug_to_external_db_map_filepath = '../data/P1-03-TTD_crossmatching.txt'
    parsed_ttd_drug_to_external_db_map = parse_ttd_drug_to_external_db_map_file(ttd_drug_to_external_db_map_filepath)
    with open('../out/drug_external_dbs.json', 'w+') as out_stream:
        json.dump(parsed_ttd_drug_to_external_db_map, out_stream, indent=4)

if __name__ == '__main__':
    main()
