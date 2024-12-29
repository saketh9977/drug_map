create user :POSTGRES_NONROOT_USER with password :'POSTGRES_NONROOT_PASSWORD';
create database :POSTGRES_NONROOT_DB;
grant all privileges on database :POSTGRES_NONROOT_DB to :POSTGRES_NONROOT_USER;

\c :POSTGRES_NONROOT_DB;

create schema ttd authorization :POSTGRES_NONROOT_USER;
set role :POSTGRES_NONROOT_USER;
set search_path to ttd;

select current_database();
select current_schema();
select current_user;

-- create tables
\i 'sql/tables/drug.sql';
\i 'sql/tables/drug_synonym.sql';
\i 'sql/tables/disease.sql';
\i 'sql/tables/biomarker.sql';
\i 'sql/tables/drug_disease.sql';
\i 'sql/tables/biomarker_disease.sql';