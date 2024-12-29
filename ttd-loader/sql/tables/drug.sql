create table ttd.drug(
    id varchar(7),
    name_ varchar(512),
    chemical_formula varchar(64),
    pubchem_cid varchar(8),
    pubchem_sid varchar(5120),
    cas_number varchar(16),
    chebi_id varchar(16),
    superdrug_atc varchar(128),
    superdrug_cas varchar(16),
    primary key(id)
);