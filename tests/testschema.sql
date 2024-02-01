--
-- PostgreSQL database dump
--

-- Dumped from database version 15.4
-- Dumped by pg_dump version 15.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: bannertype; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.bannertype AS ENUM (
    'INFO',
    'WARNING'
);


ALTER TYPE public.bannertype OWNER TO rob;

--
-- Name: command; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.command AS ENUM (
    'GET_USER',
    'SEND_USER',
    'GET_ORG',
    'SEND_ORG',
    'GET_PROJECT',
    'SEND_PROJECT',
    'GET_TEAM',
    'SEND_TEAM',
    'GET_TASK',
    'SEND_TASK'
);


ALTER TYPE public.command OWNER TO rob;

--
-- Name: editors; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.editors AS ENUM (
    'ID',
    'JOSM',
    'POTLATCH_2',
    'FIELD_PAPERS',
    'CUSTOM',
    'RAPID'
);


ALTER TYPE public.editors OWNER TO rob;

--
-- Name: encouragingemailtype; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.encouragingemailtype AS ENUM (
    'PROJECT_PROGRESS',
    'PROJECT_COMPLETE',
    'BEEN_SOME_TIME'
);


ALTER TYPE public.encouragingemailtype OWNER TO rob;

--
-- Name: mappinglevel; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.mappinglevel AS ENUM (
    'BEGINNER',
    'INTERMEDIATE',
    'ADVANCED'
);


ALTER TYPE public.mappinglevel OWNER TO rob;

--
-- Name: mappingnotallowed; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.mappingnotallowed AS ENUM (
    'USER_ALREADY_HAS_TASK_LOCKED',
    'USER_NOT_CORRECT_MAPPING_LEVEL',
    'USER_NOT_ACCEPTED_LICENSE',
    'USER_NOT_ALLOWED',
    'PROJECT_NOT_PUBLISHED',
    'USER_NOT_TEAM_MEMBER',
    'PROJECT_HAS_NO_OSM_TEAM',
    'NOT_A_MAPPING_TEAM'
);


ALTER TYPE public.mappingnotallowed OWNER TO rob;

--
-- Name: mappingtypes; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.mappingtypes AS ENUM (
    'ROADS',
    'BUILDINGS',
    'WATERWAYS',
    'LAND_USE',
    'OTHER'
);


ALTER TYPE public.mappingtypes OWNER TO rob;

--
-- Name: notification; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.notification AS ENUM (
    'BAD_DATA',
    'BLOCKED_USER',
    'PROJECT_FINISHED'
);


ALTER TYPE public.notification OWNER TO rob;

--
-- Name: organisationtype; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.organisationtype AS ENUM (
    'FREE',
    'DISCOUNTED',
    'FULL_FEE'
);


ALTER TYPE public.organisationtype OWNER TO rob;

--
-- Name: organizationtype; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.organizationtype AS ENUM (
    'FREE',
    'DISCOUNTED',
    'FULL_FEE'
);


ALTER TYPE public.organizationtype OWNER TO rob;

--
-- Name: permissions; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.permissions AS ENUM (
    'ANY_PERMISSIONS',
    'LEVEL',
    'TEAMS',
    'TEAMS_LEVEL'
);


ALTER TYPE public.permissions OWNER TO rob;

--
-- Name: projectdifficulty; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.projectdifficulty AS ENUM (
    'EASY',
    'MODERATE',
    'CHALLENGING'
);


ALTER TYPE public.projectdifficulty OWNER TO rob;

--
-- Name: projectpriority; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.projectpriority AS ENUM (
    'URGENT',
    'HIGH',
    'MEDIUM',
    'LOW'
);


ALTER TYPE public.projectpriority OWNER TO rob;

--
-- Name: projectstatus; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.projectstatus AS ENUM (
    'ARCHIVED',
    'PUBLISHED',
    'DRAFT'
);


ALTER TYPE public.projectstatus OWNER TO rob;

--
-- Name: taskaction; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.taskaction AS ENUM (
    'RELEASED_FOR_MAPPING',
    'LOCKED_FOR_MAPPING',
    'MARKED_MAPPED',
    'LOCKED_FOR_VALIDATION',
    'VALIDATED',
    'MARKED_INVALID',
    'MARKED_BAD',
    'SPLIT_NEEDED',
    'RECREATED',
    'COMMENT'
);


ALTER TYPE public.taskaction OWNER TO rob;

--
-- Name: taskcreationmode; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.taskcreationmode AS ENUM (
    'GRID',
    'CREATE_ROADS',
    'UPLOAD'
);


ALTER TYPE public.taskcreationmode OWNER TO rob;

--
-- Name: taskstatus; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.taskstatus AS ENUM (
    'READY',
    'TASK_LOCKED_FOR_MAPPING',
    'TASK_STATUS_MAPPED',
    'TASK_LOCKED_FOR_VALIDATION',
    'TASK_VALIDATED',
    'TASK_INVALIDATED',
    'BAD',
    'SPLIT',
    'TASK_ARCHIVED'
);


ALTER TYPE public.taskstatus OWNER TO rob;

--
-- Name: teamjoinmethod; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.teamjoinmethod AS ENUM (
    'ANY_METHOD',
    'BY_REQUEST',
    'BY_INVITE'
);


ALTER TYPE public.teamjoinmethod OWNER TO rob;

--
-- Name: teammemberfunctions; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.teammemberfunctions AS ENUM (
    'MANAGER',
    'MEMBER'
);


ALTER TYPE public.teammemberfunctions OWNER TO rob;

--
-- Name: teamroles; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.teamroles AS ENUM (
    'TEAM_READ_ONLY',
    'TEAM_MAPPER',
    'TEAM_VALIDATOR',
    'PROJECT_MANAGER'
);


ALTER TYPE public.teamroles OWNER TO rob;

--
-- Name: teamvisibility; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.teamvisibility AS ENUM (
    'PUBLIC',
    'PRIVATE'
);


ALTER TYPE public.teamvisibility OWNER TO rob;

--
-- Name: usergender; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.usergender AS ENUM (
    'MALE',
    'FEMALE',
    'SELF_DESCRIBE',
    'PREFER_NOT'
);


ALTER TYPE public.usergender OWNER TO rob;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.userrole AS ENUM (
    'USER_READ_ONLY',
    'USER_MAPPER',
    'ADMIN',
    'PROJECT_VALIDATOR',
    'FIELD_ADMIN',
    'ORGANIZATION_ADMIN'
);


ALTER TYPE public.userrole OWNER TO rob;

--
-- Name: validatingnotallowed; Type: TYPE; Schema: public; Owner: rob
--

CREATE TYPE public.validatingnotallowed AS ENUM (
    'USER_NOT_VALIDATOR',
    'USER_LICENSE_NOT_ACCEPTED',
    'USER_NOT_ON_ALLOWED_LIST',
    'PROJECT_NOT_YET_PUBLISHED',
    'USER_IS_BEGINNER',
    'NOT_A_VALIDATION_TEAM',
    'USER_NOT_IN_TEAM',
    'PROJECT_HAS_NO_TEAM',
    'USER_ALREADY_LOCKED_TASK'
);


ALTER TYPE public.validatingnotallowed OWNER TO rob;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: organizations; Type: TABLE; Schema: public; Owner: rob
--

CREATE TABLE public.organizations (
    id bigint NOT NULL,
    name character varying NOT NULL,
    slug character varying NOT NULL,
    logo character varying,
    description character varying,
    url character varying,
    subscription_tier integer NOT NULL
);


ALTER TABLE public.organizations OWNER TO rob;

--
-- Name: organizations_id_seq; Type: SEQUENCE; Schema: public; Owner: rob
--

CREATE SEQUENCE public.organizations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organizations_id_seq OWNER TO rob;

--
-- Name: projects; Type: TABLE; Schema: public; Owner: rob
--

CREATE TABLE public.projects (
    id bigint NOT NULL,
    odkid bigint,
    author_id bigint NOT NULL,
    created timestamp without time zone NOT NULL,
    project_name_prefix character varying,
    task_type_prefix character varying,
    location_str character varying,
    geometry polygon,
    last_updated timestamp without time zone,
    due_date timestamp without time zone,
    total_tasks integer,
    tasks_mapped integer,
    tasks_validated integer,
    enforce_random_task_selection boolean,
    country character varying[],
    rapid_power_user boolean,
    progress_email_sent boolean,
    tasks_bad_imagery integer,
    odk_central_src character varying,
    xform_title character varying,
    private boolean,
    featured boolean,
    organisation_id integer,
    changeset_comment character varying,
    osmcha_filter_id character varying,
    imagery character varying,
    default_locale character varying,
    osm_preset character varying,
    odk_preset character varying,
    josm_preset character varying,
    id_presets character varying[],
    extra_id_params character varying,
    license_id integer,
    centroid point,
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


ALTER TABLE public.projects OWNER TO rob;

--
-- Name: projects_id_seq; Type: SEQUENCE; Schema: public; Owner: rob
--

CREATE SEQUENCE public.projects_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.projects_id_seq OWNER TO rob;

--
-- Name: schemas; Type: TABLE; Schema: public; Owner: fmtm
--

CREATE TABLE public.schemas (
    schema character varying,
    version double precision
);


ALTER TABLE public.schemas OWNER TO fmtm;

--
-- Name: tasks; Type: TABLE; Schema: public; Owner: rob
--

CREATE TABLE public.tasks (
    id bigint NOT NULL,
    project_id integer NOT NULL,
    project_task_index integer,
    project_task_name character varying,
    outline polygon,
    geometry polygon,
    initial_feature_count integer,
    locked_by bigint,
    mapped_by bigint,
    validated_by bigint,
    qr_code_id integer,
    is_square boolean,
    extra_properties character varying,
    x integer,
    y integer,
    zoom integer
);


ALTER TABLE public.tasks OWNER TO rob;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: rob
--

CREATE SEQUENCE public.tasks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO rob;

--
-- Name: teams; Type: TABLE; Schema: public; Owner: rob
--

CREATE TABLE public.teams (
    id bigint NOT NULL,
    organisation_id integer NOT NULL,
    name character varying NOT NULL,
    logo character varying,
    description character varying,
    invite_only boolean,
    visibility public.teamvisibility NOT NULL,
    join_method integer
);


ALTER TABLE public.teams OWNER TO rob;

--
-- Name: teams_id_seq; Type: SEQUENCE; Schema: public; Owner: rob
--

CREATE SEQUENCE public.teams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.teams_id_seq OWNER TO rob;

--
-- Name: users; Type: TABLE; Schema: public; Owner: rob
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    username character varying,
    name character varying NOT NULL,
    city character varying,
    country character varying,
    email_address character varying,
    is_email_verified boolean,
    is_expert boolean,
    tasks_notifications boolean,
    role public.userrole,
    mapping_level public.mappinglevel NOT NULL,
    tasks_mapped integer,
    tasks_validated integer,
    tasks_invalidated integer,
    projects_mapped integer[],
    date_registered timestamp without time zone,
    last_validation_date timestamp without time zone,
    password character varying,
    osm_id bigint,
    facebook_id character varying,
    irc_id character varying,
    skype_id character varying,
    slack_id character varying,
    linkedin_id character varying,
    twitter_id character varying,
    default_editor character varying,
    picture_url character varying,
    gender integer,
    mentions_notifications boolean,
    projects_notifications boolean,
    self_description_gender character varying,
    projects_comments_notifications boolean,
    tasks_comments_notifications boolean,
    teams_announcement_notifications boolean
);


ALTER TABLE public.users OWNER TO rob;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: rob
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO rob;

--
-- Name: organizations organizations_id_key; Type: CONSTRAINT; Schema: public; Owner: rob
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_id_key UNIQUE (id);


--
-- Name: projects projects_id_key; Type: CONSTRAINT; Schema: public; Owner: rob
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_id_key UNIQUE (id);


--
-- Name: teams teams_id_key; Type: CONSTRAINT; Schema: public; Owner: rob
--

ALTER TABLE ONLY public.teams
    ADD CONSTRAINT teams_id_key UNIQUE (id);


--
-- Name: users users_id_key; Type: CONSTRAINT; Schema: public; Owner: rob
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_id_key UNIQUE (id);


--
-- PostgreSQL database dump complete
--

