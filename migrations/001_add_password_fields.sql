-- Migración de ejemplo: agregar campos para password y token de recuperación
ALTER TABLE personal
  ADD COLUMN password_hash TEXT;

ALTER TABLE personal
  ADD COLUMN password_reset_token TEXT;

ALTER TABLE personal
  ADD COLUMN password_reset_expires_at TIMESTAMP;

-- Opcional: índice para búsquedas por token
CREATE INDEX IF NOT EXISTS idx_personal_reset_token ON personal(password_reset_token);

