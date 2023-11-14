DROP TABLE IF EXISTS public.organisation_managers CASCADE;
CREATE TABLE public.organisation_managers (
    organisation_id integer NOT NULL,
    user_id bigint NOT NULL
);

DROP TABLE IF EXISTS public.organisations CASCADE;
CREATE TABLE public.organisations (
    id integer NOT NULL,
    name character varying(512) NOT NULL,
    slug character varying(255) NOT NULL,
    logo character varying,
    description character varying,
    url character varying,
    type public.organisationtype NOT NULL
);
ALTER TABLE public.organisations OWNER TO fmtm;
CREATE SEQUENCE public.organisations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.organisations_id_seq OWNER TO fmtm;
ALTER SEQUENCE public.organisations_id_seq OWNED BY public.organisations.id;

