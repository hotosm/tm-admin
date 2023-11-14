CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS public.projects CASCADE;
CREATE TABLE public.projects (
    id integer NOT NULL,
    odkid integer,
    author_id bigint NOT NULL,
    created timestamp without time zone NOT NULL,
    task_creation_mode public.taskcreationmode NOT NULL,
    project_name_prefix character varying,
    task_type_prefix character varying,
    location_str character varying,
    outline public.geometry(Polygon,4326),
    last_updated timestamp without time zone,
    status public.projectstatus NOT NULL,
    total_tasks integer,
    odk_central_src character varying,
    xform_title character varying,
    private boolean,
    mapper_level public.mappinglevel NOT NULL,
    priority public.projectpriority,
    featured boolean,
    mapping_permissions public.permissions,
    validation_permission public.permissions,
    organisation_id integer,
    changeset_comment character varying,
    osmcha_filter_id character varying,
    imagery character varying,
    osm_preset character varying,
    odk_preset character varying,
    josm_preset character varying,
    id_presets character varying[],
    extra_id_params character varying,
    license_id integer,
    centroid public.geometry(Point,4326),
    odk_central_url character varying,
    odk_central_user character varying,
    odk_central_password character varying,
    extract_completed_count integer,
    form_xls bytea,
    form_config_file bytea,
    data_extract_type character varying,
    task_split_type character varying,
    hashtags character varying[]
);
ALTER TABLE public.projects OWNER TO fmtm;
CREATE SEQUENCE public.projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.projects_id_seq OWNER TO fmtm;
ALTER SEQUENCE public.projects_id_seq OWNED BY public.projects.id;

