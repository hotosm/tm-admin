-- Do not edit this file, it's generated from the yaml file

DROP TABLE IF EXISTS public.tasks CASCADE;
CREATE TABLE public.tasks (
	id bigint NOT NULL,
	project_id integer NOT NULL,
	project_task_index integer,
	project_task_name character varying,
	outline public.geometry(Polygon,4326),
	geometry_geojson character varying,
	initial_feature_count integer,
	task_status public.taskstatus,
	locked_by bigint,
	mapped_by bigint,
	validated_by bigint,
	qr_code_id integer
);

DROP SEQUENCE IF EXISTS public.users_id_seq CASCADE;
CREATE SEQUENCE public.users_id_seq
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;
