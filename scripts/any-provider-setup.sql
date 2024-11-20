-- Any script that should be run as the provider, such as creating and populating database objects that need to be shared with the application package.
-- This script must be idempotent.

CREATE DATABASE IF NOT EXISTS PENGUINS_ML_APP;

-- Schemas
-- data schema
CREATE SCHEMA IF NOT EXISTS PENGUINS_ML_APP.DATA;
-- create schema to hold all stages
CREATE SCHEMA IF NOT EXISTS PENGUINS_ML_APP.STAGES;
-- create schema to hold all file formats
CREATE SCHEMA IF NOT EXISTS PENGUINS_ML_APP.FILE_FORMATS;
-- apps to hold all streamlit apps
CREATE SCHEMA IF NOT EXISTS PENGUINS_ML_APP.APPS;

-- Stages and File Format
-- add an external stage to a s3 bucket
CREATE STAGE IF NOT EXISTS PENGUINS_ML_APP.STAGES.PENGUINS
  URL='s3://sfquickstarts/misc';

-- default CSV file format and allow values to quoted by "
CREATE FILE FORMAT IF NOT EXISTS PENGUINS_ML_APP.FILE_FORMATS.CSV
  TYPE='CSV'
  SKIP_HEADER=1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"';

-- Create table to hold penguins data
CREATE OR ALTER TABLE  PENGUINS_ML_APP.DATA.PENGUINS(
   SPECIES STRING NOT NULL,
   ISLAND STRING NOT NULL,
   BILL_LENGTH_MM NUMBER NOT NULL,
   BILL_DEPTH_MM NUMBER NOT NULL,
   FLIPPER_LENGTH_MM NUMBER NOT NULL,
   BODY_MASS_G NUMBER NOT NULL,
   SEX STRING NOT NULL
);

-- Load the data from penguins_cleaned.csv
COPY INTO  PENGUINS_ML_APP.DATA.PENGUINS
FROM @PENGUINS_ML_APP.STAGES.PENGUINS/penguins_cleaned.csv
FILE_FORMAT=(FORMAT_NAME='PENGUINS_ML_APP.FILE_FORMATS.CSV');
