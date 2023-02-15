Postgres:
    tables/
        archives/
            create:
                -- Table: public.archives

                -- DROP TABLE IF EXISTS public.archives;

                CREATE TABLE IF NOT EXISTS public.archives
                (
                    id integer NOT NULL DEFAULT nextval('archives_id_seq'::regclass),
                    name character varying COLLATE pg_catalog."default" NOT NULL,
                    data bytea NOT NULL,
                    deleted boolean,
                    deleted_at timestamp without time zone,
                    CONSTRAINT archives_pkey PRIMARY KEY (id)
                )

                TABLESPACE pg_default;

                ALTER TABLE IF EXISTS public.archives
                    OWNER to postgres;
            sequence:
                -- SEQUENCE: public.archives_id_seq

                -- DROP SEQUENCE IF EXISTS public.archives_id_seq;

                CREATE SEQUENCE IF NOT EXISTS public.archives_id_seq
                    INCREMENT 1
                    START 1
                    MINVALUE 1
                    MAXVALUE 2147483647
                    CACHE 1
                    OWNED BY archives.id;

                ALTER SEQUENCE public.archives_id_seq
                    OWNER TO postgres;
        images/
            create:
                -- Table: public.images

                -- DROP TABLE IF EXISTS public.images;

                CREATE TABLE IF NOT EXISTS public.images
                (
                    id integer NOT NULL DEFAULT nextval('images_id_seq'::regclass),
                    name character varying COLLATE pg_catalog."default" NOT NULL,
                    data bytea NOT NULL,
                    deleted boolean,
                    deleted_at timestamp without time zone,
                    CONSTRAINT images_pkey PRIMARY KEY (id)
                )

                TABLESPACE pg_default;

                ALTER TABLE IF EXISTS public.images
                    OWNER to postgres;
            sequence:
                -- SEQUENCE: public.images_id_seq

                -- DROP SEQUENCE IF EXISTS public.images_id_seq;

                CREATE SEQUENCE IF NOT EXISTS public.images_id_seq
                    INCREMENT 1
                    START 1
                    MINVALUE 1
                    MAXVALUE 2147483647
                    CACHE 1
                    OWNED BY images.id;

                ALTER SEQUENCE public.images_id_seq
                    OWNER TO postgres;
            constrains:
                -- Constraint: images_pkey

                -- ALTER TABLE IF EXISTS public.images DROP CONSTRAINT IF EXISTS images_pkey;

                ALTER TABLE IF EXISTS public.images
                    ADD CONSTRAINT images_pkey PRIMARY KEY (id);