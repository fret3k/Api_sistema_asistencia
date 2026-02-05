-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.asistencias (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  personal_id uuid NOT NULL,
  fecha date NOT NULL DEFAULT CURRENT_DATE,
  marca_tiempo timestamp with time zone NOT NULL,
  tipo_registro character varying NOT NULL CHECK (tipo_registro::text = ANY (ARRAY['ENTRADA_M'::text, 'SALIDA_M'::text, 'ENTRADA_T'::text, 'SALIDA_T'::text])),
  estado character varying NOT NULL CHECK (estado::text = ANY (ARRAY['A TIEMPO'::character varying, 'TARDE'::character varying, 'NORMAL'::character varying, 'SALIDA_ANTICIPADA'::character varying]::text[])),
  motivo text,
  CONSTRAINT asistencias_pkey PRIMARY KEY (id),
  CONSTRAINT asistencias_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id)
);
CREATE TABLE public.codificacion_facial (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  personal_id uuid NOT NULL UNIQUE,
  embedding ARRAY NOT NULL,
  created_at timestamp with time zone NOT NULL,
  updated_at timestamp with time zone NOT NULL,
  CONSTRAINT codificacion_facial_pkey PRIMARY KEY (id),
  CONSTRAINT codificacion_facial_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id)
);
CREATE TABLE public.control_tiempo (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  personal_id uuid NOT NULL,
  tipo_registro character varying NOT NULL CHECK (tipo_registro::text = ANY (ARRAY['ENTRADA'::character varying, 'SALIDA'::character varying]::text[])),
  fecha date NOT NULL,
  hora time without time zone NOT NULL,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT control_tiempo_pkey PRIMARY KEY (id),
  CONSTRAINT control_tiempo_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id)
);
CREATE TABLE public.fotos_perfil (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  personal_id uuid NOT NULL UNIQUE,
  foto_base64 text NOT NULL,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT fotos_perfil_pkey PRIMARY KEY (id),
  CONSTRAINT fotos_perfil_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id)
);
CREATE TABLE public.personal (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  dni character varying NOT NULL UNIQUE,
  nombre character varying NOT NULL,
  apellido_paterno character varying NOT NULL,
  apellido_materno character varying NOT NULL,
  email character varying NOT NULL UNIQUE,
  es_administrador boolean NOT NULL DEFAULT false,
  password_hash text NOT NULL,
  password_reset_token text,
  password_reset_expires_at timestamp with time zone,
  CONSTRAINT personal_pkey PRIMARY KEY (id)
);
CREATE TABLE public.solicitudes_ausencias (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  personal_id uuid NOT NULL,
  tipo_ausencia character varying NOT NULL,
  fecha_inicio date NOT NULL,
  fecha_fin date NOT NULL,
  hora_inicio time without time zone,
  hora_fin time without time zone,
  razon text NOT NULL,
  estado_solicitud character varying NOT NULL CHECK (estado_solicitud::text = ANY (ARRAY['PENDIENTE'::character varying, 'APROBADA'::character varying, 'DENEGADA'::character varying, 'ANULADA'::character varying]::text[])),
  fecha_solicitud timestamp with time zone DEFAULT now(),
  CONSTRAINT solicitudes_ausencias_pkey PRIMARY KEY (id),
  CONSTRAINT solicitudes_ausencias_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id)
);
CREATE TABLE public.solicitudes_sobretiempo (
  id uuid NOT NULL DEFAULT uuid_generate_v4(),
  personal_id uuid NOT NULL,
  fecha_trabajo date NOT NULL,
  horas_solicitadas numeric NOT NULL,
  razon text NOT NULL,
  estado_solicitud character varying NOT NULL CHECK (estado_solicitud::text = ANY (ARRAY['PENDIENTE'::character varying, 'APROBADA'::character varying, 'DENEGADA'::character varying, 'ANULADA'::character varying]::text[])),
  fecha_solicitud timestamp with time zone DEFAULT now(),
  CONSTRAINT solicitudes_sobretiempo_pkey PRIMARY KEY (id),
  CONSTRAINT solicitudes_sobretiempo_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES public.personal(id)
);
-- 