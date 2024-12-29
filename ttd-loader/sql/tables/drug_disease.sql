create table ttd.drug_disease(
    drug_id varchar(7) references ttd.drug(id),
    disease_name varchar(256) references ttd.disease(name_),
    clinical_status varchar(32),
    primary key(drug_id, disease_name)
);