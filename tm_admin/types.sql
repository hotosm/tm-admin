DROP TYPE IF EXISTS public.userrole CASCADE;
CREATE TYPE public.userrole AS ENUM (
    'MAPPER',
    'ADMIN',
    'VALIDATOR',
    'FIELD_ADMIN',
    'ORGANIZATION_ADMIN',
    'READ_ONLY'
);
ALTER TYPE public.userrole OWNER TO fmtm;

DROP TYPE IF EXISTS public.mappinglevel CASCADE;
CREATE TYPE public.mappinglevel AS ENUM (
    'BEGINNER',
    'INTERMEDIATE',
    'ADVANCED'
);
ALTER TYPE public.mappinglevel OWNER TO fmtm;

CREATE EXTENSION IF NOT EXISTS postgis;
DROP TYPE IF EXISTS public.mappinglevel CASCADE;
CREATE TYPE public.mappinglevel AS ENUM (
    'BEGINNER',
    'INTERMEDIATE',
    'ADVANCED'
);
ALTER TYPE public.mappinglevel OWNER TO fmtm;

DROP TYPE IF EXISTS public.projectstatus CASCADE;
CREATE TYPE public.projectstatus AS ENUM (
    'ARCHIVED',
    'PUBLISHED',
    'DRAFT'
);
ALTER TYPE public.projectstatus OWNER TO fmtm;

DROP TYPE IF EXISTS public.projectpriority CASCADE;
CREATE TYPE public.projectpriority AS ENUM (
    'URGENT',
    'HIGH',
    'MEDIUM',
    'LOW'
);
ALTER TYPE public.projectpriority OWNER TO fmtm;

DROP TYPE IF EXISTS public.permissions CASCADE;
CREATE TYPE public.permissions AS ENUM (
    'ANY',
    'LEVEL',
    'TEAMS',
    'TEAMS_LEVEL'
);
ALTER TYPE public.permissions OWNER TO fmtm;

-- DROP TYPE IF EXISTS public.validationpermission CASCADE;
-- CREATE TYPE public.validationpermission AS ENUM (
--     'ANY',
--     'LEVEL',
--     'TEAMS',
--     'TEAMS_LEVEL'
-- );
-- ALTER TYPE public.validationpermission OWNER TO fmtm;
--
DROP TYPE IF EXISTS public.taskcreationmode CASCADE;
CREATE TYPE public.taskcreationmode AS ENUM (
    'GRID',
    'ROADS',
    'UPLOAD'
);
ALTER TYPE public.taskcreationmode OWNER TO fmtm;

DROP TYPE IF EXISTS public.organisationtype CASCADE;
CREATE TYPE public.organisationtype AS ENUM (
    'FREE',
    'DISCOUNTED',
    'FULL_FEE'
);

DROP TYPE IF EXISTS public.teamvisibility CASCADE;
CREATE TYPE public.teamvisibility AS ENUM (
    'PUBLIC',
    'PRIVATE'
);
ALTER TYPE public.teamvisibility OWNER TO fmtm;

DROP TYPE IF EXISTS public.taskaction CASCADE;
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
ALTER TYPE public.taskaction OWNER TO fmtm;

DROP TYPE IF EXISTS public.taskstatus CASCADE;
CREATE TYPE public.taskstatus AS ENUM (
    'READY',
    'TASK_LOCKED_FOR_MAPPING',
    'MAPPED',
    'TASK_LOCKED_FOR_VALIDATION',
    'TASK_VALIDATED',
    'TASK_INVALIDATED',
    'BAD',
    'SPLIT',
    'TASK_ARCHIVED'
);
ALTER TYPE public.taskstatus OWNER TO fmtm;


