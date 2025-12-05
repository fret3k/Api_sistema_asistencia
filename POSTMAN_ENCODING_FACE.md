# Guía de Postman - API Sistema de Asistencia

## Configuración Base
- **Base URL**: `http://localhost:8000` (ajusta según tu configuración)
- **Content-Type**: `application/json`
- **Documentación Interactiva**: 
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

---

## 📋 Índice
1. [Personal - Registrar con Codificación Facial](#1-registrar-personal-con-codificación-facial)
2. [Encoding Face - Endpoints](#encoding-face-endpoints)
   - [Crear Codificación Facial](#2-crear-codificación-facial)
   - [Listar Todas](#3-listar-todas-las-codificaciones)
   - [Obtener por ID](#4-obtener-codificación-por-id)
   - [Obtener por Personal ID](#5-obtener-codificaciones-por-personal-id)
   - [Eliminar](#6-eliminar-codificación-facial)

---

## 1. Registrar Personal con Codificación Facial
**POST** `/personal/register-with-encoding`

### Descripción:
Endpoint combinado que registra un nuevo personal junto con su codificación facial en una sola operación. Ideal para el registro inicial de empleados.

### Headers:
```
Content-Type: application/json
```

### Body (JSON):
```json
{
  "dni": "12345678",
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "email": "juan.perez@example.com",
  "es_administrador": false,
  "password": "MiPassword123",
  "embedding": [0.123, -0.456, 0.789, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901]
}
```

### Notas:
- **dni**: Documento Nacional de Identidad
- **password**: Mínimo 8 caracteres (se hashea automáticamente)
- **embedding**: Array de números flotantes (vector de 128 valores para embeddings faciales)

### Ejemplo de respuesta (201):
```json
{
  "personal_id": "123e4567-e89b-12d3-a456-426614174000",
  "encoding_id": "987e6543-e21b-34c5-d678-123456789abc",
  "message": "Personal y codificación facial registrados correctamente"
}
```

### Errores posibles:
- **400**: Error al registrar (email duplicado, datos inválidos, etc.)
- **422**: Error de validación (campos faltantes o inválidos)

---

## Encoding Face - Endpoints

---

## 2. Crear Codificación Facial
**POST** `/encoding-face/`

### Headers:
```
Content-Type: application/json
```

### Body (JSON):
```json
{
  "personal_id": "123e4567-e89b-12d3-a456-426614174000",
  "embedding": [0.123, -0.456, 0.789, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456]
}
```

### Notas:
- `personal_id`: UUID válido de un personal existente
- `embedding`: Array de números flotantes (vector de 128 valores para embeddings faciales)

### Ejemplo de respuesta (201):
```json
{
  "id": "987e6543-e21b-34c5-d678-123456789abc",
  "personal_id": "123e4567-e89b-12d3-a456-426614174000",
  "embedding": [0.123, -0.456, 0.789, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456]
}
```

---

## 3. Listar Todas las Codificaciones
**GET** `/encoding-face/`

### Headers:
```
(ninguno requerido)
```

### Body:
(ninguno)

### Ejemplo de respuesta (200):
```json
[
  {
    "id": "987e6543-e21b-34c5-d678-123456789abc",
    "personal_id": "123e4567-e89b-12d3-a456-426614174000",
    "embedding": [0.123, -0.456, 0.789, ...]
  },
  {
    "id": "111e2222-e33b-44c5-d666-777888999aaa",
    "personal_id": "123e4567-e89b-12d3-a456-426614174000",
    "embedding": [0.234, -0.567, 0.890, ...]
  }
]
```

---

## 4. Obtener Codificación por ID
**GET** `/encoding-face/{id}`

### Parámetros de URL:
- `id`: UUID de la codificación facial

### Ejemplo:
```
GET http://localhost:8000/encoding-face/987e6543-e21b-34c5-d678-123456789abc
```

### Ejemplo de respuesta (200):
```json
{
  "id": "987e6543-e21b-34c5-d678-123456789abc",
  "personal_id": "123e4567-e89b-12d3-a456-426614174000",
  "embedding": [0.123, -0.456, 0.789, ...]
}
```

### Error (404):
```json
{
  "detail": "Codificación facial no encontrada"
}
```

---

## 5. Obtener Codificaciones por Personal ID
**GET** `/encoding-face/personal/{personal_id}`

### Parámetros de URL:
- `personal_id`: UUID del personal

### Ejemplo:
```
GET http://localhost:8000/encoding-face/personal/123e4567-e89b-12d3-a456-426614174000
```

### Ejemplo de respuesta (200):
```json
[
  {
    "id": "987e6543-e21b-34c5-d678-123456789abc",
    "personal_id": "123e4567-e89b-12d3-a456-426614174000",
    "embedding": [0.123, -0.456, 0.789, ...]
  },
  {
    "id": "111e2222-e33b-44c5-d666-777888999aaa",
    "personal_id": "123e4567-e89b-12d3-a456-426614174000",
    "embedding": [0.234, -0.567, 0.890, ...]
  }
]
```

---

## 6. Eliminar Codificación Facial
**DELETE** `/encoding-face/{id}`

### Parámetros de URL:
- `id`: UUID de la codificación facial a eliminar

### Ejemplo:
```
DELETE http://localhost:8000/encoding-face/987e6543-e21b-34c5-d678-123456789abc
```

### Ejemplo de respuesta (200):
```json
{
  "message": "Codificación facial eliminada correctamente"
}
```

---

## Colección de Postman (JSON)

Puedes importar esta colección directamente en Postman:

```json
{
  "info": {
    "name": "Encoding Face API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Crear Codificación Facial",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"personal_id\": \"123e4567-e89b-12d3-a456-426614174000\",\n  \"embedding\": [0.123, -0.456, 0.789, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456]\n}"
        },
        "url": {
          "raw": "{{base_url}}/encoding-face/",
          "host": ["{{base_url}}"],
          "path": ["encoding-face", ""]
        }
      }
    },
    {
      "name": "Listar Todas",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/encoding-face/",
          "host": ["{{base_url}}"],
          "path": ["encoding-face", ""]
        }
      }
    },
    {
      "name": "Obtener por ID",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/encoding-face/:id",
          "host": ["{{base_url}}"],
          "path": ["encoding-face", ":id"],
          "variable": [
            {
              "key": "id",
              "value": "987e6543-e21b-34c5-d678-123456789abc"
            }
          ]
        }
      }
    },
    {
      "name": "Obtener por Personal ID",
      "request": {
        "method": "GET",
        "url": {
          "raw": "{{base_url}}/encoding-face/personal/:personal_id",
          "host": ["{{base_url}}"],
          "path": ["encoding-face", "personal", ":personal_id"],
          "variable": [
            {
              "key": "personal_id",
              "value": "123e4567-e89b-12d3-a456-426614174000"
            }
          ]
        }
      }
    },
    {
      "name": "Eliminar",
      "request": {
        "method": "DELETE",
        "url": {
          "raw": "{{base_url}}/encoding-face/:id",
          "host": ["{{base_url}}"],
          "path": ["encoding-face", ":id"],
          "variable": [
            {
              "key": "id",
              "value": "987e6543-e21b-34c5-d678-123456789abc"
            }
          ]
        }
      }
    }
  ],
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8000"
    }
  ]
}
```

---

## Variables de Entorno en Postman

Crea una variable de entorno:
- **Variable**: `base_url`
- **Valor**: `http://localhost:8000` (o el puerto que uses)

---

## Tips para Probar

1. **Primero crea un personal** usando `/personal/` para obtener un `personal_id` válido
2. **Genera un embedding real** (128 valores es común para face_recognition)
3. **Guarda los IDs** que recibas en las respuestas para usarlos en otros endpoints
4. **Verifica que el servidor esté corriendo** antes de hacer las peticiones

