-- Creación de las tablas principales para Supabase/Postgres

-- 1. Tabla personal
CREATE TABLE IF NOT EXISTS personal (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dni VARCHAR(15) UNIQUE NOT NULL,
    nombre_completo VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    es_administrador BOOLEAN NOT NULL DEFAULT FALSE,
    password_hash TEXT NOT NULL,
    codificacion_facial REAL[]
);

-- 2. Tabla asistencias
CREATE TABLE IF NOT EXISTS asistencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    personal_id UUID REFERENCES personal(id) NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    marca_tiempo TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    tipo_registro VARCHAR(20) NOT NULL CHECK (tipo_registro IN (
        'ENTRADA_M',
        'SALIDA_M',
        'ENTRADA_T',
        'SALIDA_T'
    )),
    estado VARCHAR(50) NOT NULL CHECK (
        estado IN (
            'A TIEMPO',
            'TARDE',
            'SALIDA_ANTICIPADA',
            'OMISION'
        )
    ),
    motivo TEXT
);

-- 3. Tabla solicitudes_ausencias
CREATE TABLE IF NOT EXISTS solicitudes_ausencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    personal_id UUID REFERENCES personal(id) NOT NULL,
    tipo_ausencia VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    hora_inicio TIME,
    hora_fin TIME,
    razon TEXT NOT NULL,
    estado_solicitud VARCHAR(50) NOT NULL CHECK (estado_solicitud IN ('PENDIENTE', 'APROBADA', 'DENEGADA', 'ANULADA')),
    fecha_solicitud TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tabla solicitudes_sobretiempo
CREATE TABLE IF NOT EXISTS solicitudes_sobretiempo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    personal_id UUID REFERENCES personal(id) NOT NULL,
    fecha_trabajo DATE NOT NULL,
    horas_solicitadas DECIMAL(4, 2) NOT NULL,
    razon TEXT NOT NULL,
    estado_solicitud VARCHAR(50) NOT NULL CHECK (estado_solicitud IN ('PENDIENTE', 'APROBADA', 'DENEGADA', 'ANULADA')),
    fecha_solicitud TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Índices
CREATE INDEX IF NOT EXISTS idx_asistencias_personal ON asistencias (personal_id);
CREATE INDEX IF NOT EXISTS idx_ausencias_personal ON solicitudes_ausencias (personal_id, estado_solicitud);
CREATE INDEX IF NOT EXISTS idx_sobretiempo_personal ON solicitudes_sobretiempo (personal_id, estado_solicitud);

