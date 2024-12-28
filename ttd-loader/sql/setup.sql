create database :POSTGRES_NONROOT_DB;
create user :POSTGRES_NONROOT_USER with password :'POSTGRES_NONROOT_PASSWORD';

-- list DBs
SELECT datname FROM pg_database;

