create table ttd.drug_synonym(
    drug_id varchar(7) references ttd.drug(id),
    synonym_ varchar(1024) not null,
    primary key(drug_id, synonym_)
);