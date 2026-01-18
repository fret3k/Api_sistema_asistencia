-- Migración: Crear tabla control_tiempo
-- Ejecutar este script en Supabase para crear la tabla de control de tiempo

CREATE TABLE IF NOT EXISTS control_tiempo (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    personal_id UUID NOT NULL REFERENCES personal(id) ON DELETE CASCADE,
    tipo_registro VARCHAR(20) NOT NULL CHECK (tipo_registro IN ('ENTRADA', 'SALIDA')),
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para optimizar consultas
    CONSTRAINT unique_registro_por_dia UNIQUE (personal_id, fecha, tipo_registro)
);

-- Índice para consultas por personal y fecha
CREATE INDEX IF NOT EXISTS idx_control_tiempo_personal_fecha 
ON control_tiempo(personal_id, fecha);

-- Índice para consultas por fecha
CREATE INDEX IF NOT EXISTS idx_control_tiempo_fecha 
ON control_tiempo(fecha);

-- Habilitar Row Level Security (RLS) si es necesario
ALTER TABLE control_tiempo ENABLE ROW LEVEL SECURITY;

-- Política para permitir insert a usuarios autenticados
CREATE POLICY "Permitir insert a usuarios autenticados" ON control_tiempo
    FOR INSERT
    WITH CHECK (auth.role() = 'authenticated');

-- Política para permitir select a usuarios autenticados
CREATE POLICY "Permitir select a usuarios autenticados" ON control_tiempo
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Comentarios de documentación
COMMENT ON TABLE control_tiempo IS 'Tabla para registrar entradas y salidas diarias del personal mediante reconocimiento facial';
COMMENT ON COLUMN control_tiempo.tipo_registro IS 'Tipo de registro: ENTRADA o SALIDA';
COMMENT ON COLUMN control_tiempo.fecha IS 'Fecha del registro (solo fecha, sin hora)';
COMMENT ON COLUMN control_tiempo.hora IS 'Hora del registro (formato HH:MM)';
