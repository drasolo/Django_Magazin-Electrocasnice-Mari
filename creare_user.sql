-- Baza de date, schema și userul cu care se conectează aplicația Django.
-- Se rulează ca postgres, din folderul proiectului:
--   psql -U postgres -v parola=PAROLA_DIN_.env -f creare_user.sql
-- Parola userului nu stă aici, ca să nu ajungă pe GitHub. Vine din variabila psql "parola".

CREATE DATABASE electrocasnice;

-- Comenzile de mai jos rulează în baza nou creată
\c electrocasnice

-- Tabelele Django stau în schema "django" (vezi OPTIONS din settings.py)
CREATE SCHEMA django;

CREATE USER magazin WITH ENCRYPTED PASSWORD :'parola';
GRANT ALL ON DATABASE electrocasnice TO magazin;
ALTER ROLE magazin SET search_path = django, public;
GRANT ALL ON SCHEMA django TO magazin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA django TO magazin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA django TO magazin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA django TO magazin;
