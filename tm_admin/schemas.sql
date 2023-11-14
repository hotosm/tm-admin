-- Versions of every table schema in this database
DROP TABLE IF EXISTS public.schemas CASCADE;
CREATE TABLE public.schemas (
    schema character varying,
    version float
);
ALTER TABLE public.schemas OWNER TO fmtm;

-- Note that this will reset the entire table!
INSERT INTO schemas(schema, version) VALUES('users', 1.0);
INSERT INTO schemas(schema, version) VALUES('teams', 1.0);
INSERT INTO schemas(schema, version) VALUES('tasks', 1.0);
INSERT INTO schemas(schema, version) VALUES('projects', 1.0);
INSERT INTO schemas(schema, version) VALUES('organizations', 1.0);
