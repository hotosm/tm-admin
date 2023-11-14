DROP TABLE IF EXISTS public.users;
CREATE TABLE public.users (
    id bigint NOT NULL,
    username character varying,
    role public.userrole NOT NULL,
    name character varying,
    city character varying,
    country character varying,
    email_address character varying,
    is_email_verified boolean,
    is_expert boolean,
    mapping_level public.mappinglevel NOT NULL,
    tasks_mapped integer NOT NULL,
    tasks_validated integer NOT NULL,
    tasks_invalidated integer NOT NULL,
    projects_mapped integer[],
    date_registered timestamp without time zone,
    last_validation_date timestamp without time zone,
    password character varying
);
ALTER TABLE public.users OWNER TO fmtm;

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER TABLE public.users_id_seq OWNER TO fmtm;
ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
