DROP TABLE IF EXISTS public.teams CASCADE;
CREATE TABLE public.teams (
    id integer NOT NULL,
    organisation_id integer NOT NULL,
    name character varying(512) NOT NULL,
    logo character varying,
    description character varying,
    invite_only boolean NOT NULL,
    visibility public.teamvisibility NOT NULL
);
ALTER TABLE public.teams OWNER TO fmtm;
CREATE SEQUENCE public.teams_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.teams_id_seq OWNER TO fmtm;
ALTER SEQUENCE public.teams_id_seq OWNED BY public.teams.id;

