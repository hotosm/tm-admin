CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS public.tasks CASCADE;
CREATE TABLE public.tasks (
    id integer NOT NULL,
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
ALTER TABLE public.tasks OWNER TO fmtm;
CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.tasks_id_seq OWNER TO fmtm;
ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;

