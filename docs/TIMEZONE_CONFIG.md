# Configuración de Zona Horaria

## Problema Resuelto
El sistema estaba guardando las fechas y horas en UTC (zona horaria del servidor de Supabase), lo que causaba una diferencia de 5 horas con la hora local de Colombia/Perú (UTC-5).

## Solución Implementada

### 1. Archivo de Configuración
Se creó `config/timezone_config.py` que define la zona horaria local:
```python
from datetime import timezone, timedelta

TIMEZONE_OFFSET = timedelta(hours=-5)
LOCAL_TIMEZONE = timezone(TIMEZONE_OFFSET)
```

### 2. Cambios en el Código

#### `services/asistencias_service.py`
- Se importó `LOCAL_TIMEZONE` desde la configuración
- Se cambió `datetime.now()` por `datetime.now(LOCAL_TIMEZONE)` en el método `registrar_asistencia()`
- Se agregó el campo `marca_tiempo` explícitamente al guardar en la base de datos con `ahora.isoformat()`
- Se actualizaron todos los usos de `date.today()` por `datetime.now(LOCAL_TIMEZONE).date()`

#### `controllers/asistencias_controller.py`
- Se importó `LOCAL_TIMEZONE` y `datetime`
- Se cambió `date.today()` por `datetime.now(LOCAL_TIMEZONE).date()` en el endpoint de estadísticas

### 3. Cómo Funciona

Cuando se registra una asistencia:
1. El sistema obtiene la hora actual con `datetime.now(LOCAL_TIMEZONE)` → Esto da la hora en UTC-5
2. Se extrae la fecha con `ahora.date()` → Fecha local correcta
3. Se guarda el timestamp completo con `ahora.isoformat()` → Incluye la zona horaria (-05:00)

Ejemplo de timestamp guardado:
```
2025-12-30T08:55:00-05:00
```

### 4. Ventajas
-  Las fechas y horas se guardan en la zona horaria local
-  La base de datos recibe timestamps con información de zona horaria
-  El frontend recibe las horas correctas sin necesidad de conversión
-  Centralizado en un solo archivo de configuración

### 5. Cambio de Zona Horaria
Si necesitas cambiar la zona horaria en el futuro, solo modifica el archivo `config/timezone_config.py`:

```python
# Para otra zona horaria, por ejemplo UTC-3 (Argentina)
TIMEZONE_OFFSET = timedelta(hours=-3)
```
