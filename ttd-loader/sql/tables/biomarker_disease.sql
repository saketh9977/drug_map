create table ttd.biomarker_disease(
    biomarker_id varchar(8) references ttd.biomarker(id),
    disease_name varchar(256) references ttd.disease(name_),
    primary key(biomarker_id, disease_name)
);