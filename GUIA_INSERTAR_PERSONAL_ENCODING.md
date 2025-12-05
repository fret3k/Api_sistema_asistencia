# Guía: Cómo Insertar Personal con Codificación Facial

## Endpoint Actualizado

**POST** `/personal/register-with-encoding`

Este endpoint registra un nuevo personal junto con su codificación facial en una sola operación.

---

## Estructura del Request

### Campos Requeridos

**Datos del Personal:**
- `dni` (string): Documento Nacional de Identidad
- `nombre` (string): Nombre del personal
- `apellido_paterno` (string): Apellido paterno
- `apellido_materno` (string): Apellido materno
- `email` (string, formato email): Correo electrónico (debe ser único)
- `password` (string, mínimo 8 caracteres): Contraseña del personal

**Datos de Codificación Facial:**
- `embedding` (array de floats): Vector de embedding facial (128 valores)

**Campos Opcionales:**
- `es_administrador` (boolean, default: false): Indica si el personal es administrador

---

## Ejemplos de Uso

### 1. Usando Postman

**URL:**
```
POST http://localhost:8000/personal/register-with-encoding
```

**Headers:**
```
Content-Type: application/json
```

**Body (raw JSON):**
```json
{
  "dni": "12345678",
  "nombre": "Juan",
  "apellido_paterno": "Pérez",
  "apellido_materno": "García",
  "email": "juan.perez@example.com",
  "es_administrador": false,
  "password": "MiPassword123",
  "embedding": [
    128 caracteres
    
  ]
}
```

**Respuesta Exitosa (201):**
```json
{
  "personal_id": "123e4567-e89b-12d3-a456-426614174000",
  "encoding_id": "987e6543-e21b-34c5-d678-123456789abc",
  "message": "Personal y codificación facial registrados correctamente"
}
```

---

### 2. Usando cURL

```bash
curl -X POST "http://localhost:8000/personal/register-with-encoding" \
  -H "Content-Type: application/json" \
  -d '{
    "dni": "12345678",
    "nombre": "Juan",
    "apellido_paterno": "Pérez",
    "apellido_materno": "García",
    "email": "juan.perez@example.com",
    "es_administrador": false,
    "password": "MiPassword123",
    "embedding": [0.123, -0.456, 0.789, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901, 0.234, -0.567, 0.890, 0.345, -0.678, 0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901]
  }'
```

---

### 3. Usando Python (requests)

```python
import requests
import json

url = "http://localhost:8000/personal/register-with-encoding"

# Datos del personal y embedding
data = {
    "dni": "12345678",
    "nombre": "Juan",
    "apellido_paterno": "Pérez",
    "apellido_materno": "García",
    "email": "juan.perez@example.com",
    "es_administrador": False,
    "password": "MiPassword123",
    "embedding": [
        0.123, -0.456, 0.789, 0.234, -0.567, 0.890, 0.345, -0.678,
        0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901,
        # ... continúa con 128 valores en total
    ]
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=data, headers=headers)

if response.status_code == 201:
    result = response.json()
    print(f"Personal creado: {result['personal_id']}")
    print(f"Encoding creado: {result['encoding_id']}")
    print(f"Mensaje: {result['message']}")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

---

### 4. Usando JavaScript (fetch)

```javascript
const url = 'http://localhost:8000/personal/register-with-encoding';

const data = {
  dni: "12345678",
  nombre: "Juan",
  apellido_paterno: "Pérez",
  apellido_materno: "García",
  email: "juan.perez@example.com",
  es_administrador: false,
  password: "MiPassword123",
  embedding: [
    0.123, -0.456, 0.789, 0.234, -0.567, 0.890, 0.345, -0.678,
    0.901, 0.456, 0.567, -0.789, 0.012, 0.345, -0.678, 0.901,
    // ... continúa con 128 valores en total
  ]
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data)
})
  .then(response => response.json())
  .then(data => {
    console.log('Éxito:', data);
    console.log('Personal ID:', data.personal_id);
    console.log('Encoding ID:', data.encoding_id);
  })
  .catch((error) => {
    console.error('Error:', error);
  });
```

---

## Generar Embedding Facial

Para obtener el embedding facial, necesitas usar una librería de reconocimiento facial. Ejemplo con `face_recognition`:

```python
import face_recognition
import numpy as np

# Cargar imagen
image = face_recognition.load_image_file("foto.jpg")

# Obtener encodings faciales
face_encodings = face_recognition.face_encodings(image)

if len(face_encodings) > 0:
    # Tomar el primer encoding (primer rostro encontrado)
    embedding = face_encodings[0].tolist()  # Convertir numpy array a lista
    
    # Ahora puedes usar este embedding en el request
    print(f"Embedding generado: {len(embedding)} valores")
    print(f"Primeros 5 valores: {embedding[:5]}")
else:
    print("No se encontró ningún rostro en la imagen")
```

---

## Errores Comunes

### Error 422 - Validación
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```
**Solución:** Verifica que el email tenga un formato válido.

### Error 400 - Email duplicado
```json
{
  "detail": "Error al registrar personal con codificación: ..."
}
```
**Solución:** El email ya existe en el sistema. Usa un email diferente.

### Error 422 - Password muy corto
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 8 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```
**Solución:** La contraseña debe tener al menos 8 caracteres.

### Error 422 - Embedding faltante
```json
{
  "detail": [
    {
      "loc": ["body", "embedding"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
**Solución:** Asegúrate de incluir el campo `embedding` con un array de 128 valores flotantes.

---

## Notas Importantes

1. **Embedding debe tener 128 valores**: El array `embedding` debe contener **exactamente 128 números flotantes** para modelos estándar de reconocimiento facial. Si envías menos valores (por ejemplo, solo 3), recibirás un error:
   ```json
   {
     "detail": [{
       "type": "too_short",
       "loc": ["body", "embedding"],
       "msg": "List should have at least 128 items after validation, not 3"
     }]
   }
   ```

2. **Generar embedding de prueba**: Puedes usar el script `generar_embedding_prueba.py` para generar un embedding de prueba con 128 valores aleatorios.

2. **Email único**: Cada personal debe tener un email único en el sistema.

3. **Password se hashea automáticamente**: La contraseña se hashea antes de almacenarse, no se guarda en texto plano.

4. **Transacción**: Si la creación del personal es exitosa pero falla la codificación facial, el personal se mantiene creado. Verifica ambos IDs en la respuesta.

5. **Documentación interactiva**: Puedes probar el endpoint directamente en:
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

---

## Ejemplo Completo con Embedding Real

```python
import requests
import face_recognition
import json

# 1. Generar embedding desde imagen
image = face_recognition.load_image_file("persona.jpg")
face_encodings = face_recognition.face_encodings(image)

if len(face_encodings) == 0:
    print("No se encontró ningún rostro")
    exit()

embedding = face_encodings[0].tolist()

# 2. Preparar datos
url = "http://localhost:8000/personal/register-with-encoding"
data = {
    "dni": "12345678",
    "nombre": "Juan",
    "apellido_paterno": "Pérez",
    "apellido_materno": "García",
    "email": "juan.perez@example.com",
    "es_administrador": False,
    "password": "MiPassword123",
    "embedding": embedding  # 128 valores flotantes
}

# 3. Enviar request
response = requests.post(url, json=data)

# 4. Procesar respuesta
if response.status_code == 201:
    result = response.json()
    print(f"✅ Personal registrado: {result['personal_id']}")
    print(f"✅ Encoding registrado: {result['encoding_id']}")
else:
    print(f"❌ Error {response.status_code}: {response.json()}")
```

