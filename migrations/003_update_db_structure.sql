-- Migración para actualizar la estructura de la base de datos según el esquema solicitado
-- Habilitar extensión UUID si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Actualizar tabla PERSONAL
-- Añadir campos para nombres separados si no existen
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'personal' AND column_name = 'apellido_paterno') THEN
        ALTER TABLE personal ADD COLUMN apellido_paterno VARCHAR(255) DEFAULT '';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'personal' AND column_name = 'apellido_materno') THEN
        ALTER TABLE personal ADD COLUMN apellido_materno VARCHAR(255) DEFAULT '';
    END IF;

    -- Renombrar nombre_completo a nombre si es necesario, o añadir nombre
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'personal' AND column_name = 'nombre_completo') THEN
        -- Opcional: Migrar datos si fuera necesario, aqui solo renombramos o añadimos
        ALTER TABLE personal RENAME COLUMN nombre_completo TO nombre;
    ELSIF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'personal' AND column_name = 'nombre') THEN
        ALTER TABLE personal ADD COLUMN nombre VARCHAR(255) DEFAULT '';
    END IF;
END $$;

-- 2. Tabla FOTOS_PERFIL
CREATE TABLE IF NOT EXISTS fotos_perfil (
  id UUID NOT NULL DEFAULT uuid_generate_v4(),
  personal_id UUID NOT NULL UNIQUE,
  foto_base64 TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  CONSTRAINT fotos_perfil_pkey PRIMARY KEY (id),
  CONSTRAINT fotos_perfil_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES personal(id)
);

-- 3. Tabla CODIFICACION_FACIAL
CREATE TABLE IF NOT EXISTS codificacion_facial (
  id UUID NOT NULL DEFAULT uuid_generate_v4(),
  personal_id UUID NOT NULL UNIQUE,
  embedding REAL[] NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  CONSTRAINT codificacion_facial_pkey PRIMARY KEY (id),
  CONSTRAINT codificacion_facial_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES personal(id)
);

-- 4. Actualizar tabla CONTROL_TIEMPO (Asegurar estructura)
CREATE TABLE IF NOT EXISTS control_tiempo (
  id UUID NOT NULL DEFAULT uuid_generate_v4(),
  personal_id UUID NOT NULL,
  tipo_registro VARCHAR(20) NOT NULL CHECK (tipo_registro IN ('ENTRADA', 'SALIDA')),
  fecha DATE NOT NULL,
  hora TIME NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT control_tiempo_pkey PRIMARY KEY (id),
  CONSTRAINT control_tiempo_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES personal(id)
);

-- 5. Tabla SOLICITUDES_AUSENCIAS (Asegurar existencia)
CREATE TABLE IF NOT EXISTS solicitudes_ausencias (
  id UUID NOT NULL DEFAULT uuid_generate_v4(),
  personal_id UUID NOT NULL,
  tipo_ausencia VARCHAR(50) NOT NULL,
  fecha_inicio DATE NOT NULL,
  fecha_fin DATE NOT NULL,
  hora_inicio TIME,
  hora_fin TIME,
  razon TEXT NOT NULL,
  estado_solicitud VARCHAR(50) NOT NULL CHECK (estado_solicitud IN ('PENDIENTE', 'APROBADA', 'DENEGADA', 'ANULADA')),
  fecha_solicitud TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT solicitudes_ausencias_pkey PRIMARY KEY (id),
  CONSTRAINT solicitudes_ausencias_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES personal(id)
);

-- 6. Tabla SOLICITUDES_SOBRETIEMPO (Asegurar existencia)
CREATE TABLE IF NOT EXISTS solicitudes_sobretiempo (
  id UUID NOT NULL DEFAULT uuid_generate_v4(),
  personal_id UUID NOT NULL,
  fecha_trabajo DATE NOT NULL,
  horas_solicitadas NUMERIC NOT NULL,
  razon TEXT NOT NULL,
  estado_solicitud VARCHAR(50) NOT NULL CHECK (estado_solicitud IN ('PENDIENTE', 'APROBADA', 'DENEGADA', 'ANULADA')),
  fecha_solicitud TIMESTAMP WITH TIME ZONE DEFAULT now(),
  CONSTRAINT solicitudes_sobretiempo_pkey PRIMARY KEY (id),
  CONSTRAINT solicitudes_sobretiempo_personal_id_fkey FOREIGN KEY (personal_id) REFERENCES personal(id)
);
