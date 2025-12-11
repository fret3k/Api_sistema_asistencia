from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)
from uuid import UUID

from dto.personal_dto.personal_request_dto import PersonalCreateDTO
from dto.personal_dto.personal_update_dto import PersonalUpdateDTO
from dto.personal_dto.personal_response_dto import PersonalResponseDTO
from dto.personal_dto.personal_with_encoding_dto import PersonalWithEncodingCreateDTO, PersonalWithEncodingResponseDTO
from services.personal_service import PersonalService

from pydantic import BaseModel, EmailStr, Field


class RecoverRequestDTO(BaseModel):
    email: EmailStr
    base_url: str


class ResetPasswordDTO(BaseModel):
    password: str = Field(..., min_length=8)


class LoginRequestDTO(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginResponseDTO(BaseModel):
    access_token: str
    token_type: str = "bearer"
    personal: PersonalResponseDTO


router = APIRouter(prefix="/personal", tags=["Personal"])


# -------------------------------------------------
#   CREAR PERSONAL
# -------------------------------------------------
@router.post("/", response_model=PersonalResponseDTO, status_code=201)
async def crear_personal(data: PersonalCreateDTO):
    """
    Crea un nuevo personal en el sistema.
    
    - **dni**: Documento Nacional de Identidad del personal
    - **nombre**: Nombre del personal
    - **apellido_paterno**: Apellido paterno
    - **apellido_materno**: Apellido materno
    - **email**: Correo electrónico (debe ser único)
    - **es_administrador**: Indica si el personal tiene permisos de administrador (default: false)
    - **password**: Contraseña del personal (mínimo 8 caracteres, se hashea automáticamente)
    
    El password llega en texto plano y se hashea en el servicio antes de almacenarse.
    """
    result = await PersonalService.create(data)

    if not result:
        raise HTTPException(status_code=400, detail="No se pudo crear el personal")

    # Normalizar sin exponer información sensible
    try:
        return PersonalResponseDTO.model_validate(result)
    except Exception:
        # Fallback manual si faltan claves
        filtered = {
            k: result[k] for k in (
                "id", "dni", "nombre", "apellido_paterno", "apellido_materno",
                "email", "es_administrador", "codificacion_facial"
            ) if k in result
        }
        return filtered


# -------------------------------------------------
#   REGISTRAR PERSONAL CON CODIFICACIÓN FACIAL
# -------------------------------------------------
@router.post("/register-with-encoding", response_model=PersonalWithEncodingResponseDTO, status_code=201)
async def registrar_personal_con_encoding(data: PersonalWithEncodingCreateDTO):
    """
    Registra un nuevo personal junto con su codificación facial en una sola operación.
    
    Este endpoint combina la creación de personal y su embedding facial, útil para
    el registro inicial de empleados con reconocimiento facial.
    
    **Campos del Personal:**
    - **dni**: Documento Nacional de Identidad
    - **nombre**: Nombre del personal
    - **apellido_paterno**: Apellido paterno
    - **apellido_materno**: Apellido materno
    - **email**: Correo electrónico (debe ser único)
    - **es_administrador**: Permisos de administrador (default: false)
    - **password**: Contraseña (mínimo 8 caracteres)
    
    **Campos de Codificación Facial:**
    - **embedding**: Array de números flotantes que representa el embedding facial
      (vector de 128 valores para modelos estándar de reconocimiento facial)
    
    **Nota:** Si la creación del personal es exitosa pero falla la codificación facial,
    el personal se mantiene creado. Se recomienda verificar ambos IDs en la respuesta.
    """
    try:
        # Log de datos recibidos para debug
        logger.info(f"Datos recibidos - dni: {data.dni}, nombre: {data.nombre}, email: {data.email}")
        logger.info(f"Embedding recibido - longitud: {len(data.embedding) if data.embedding else 'None'}")
        
        result = await PersonalService.create_with_encoding(data)
        logger.info(f"Registro exitoso - personal_id: {result.get('personal_id')}, encoding_id: {result.get('encoding_id')}")
        return PersonalWithEncodingResponseDTO(**result)
    except Exception as e:
        logger.error(f"Error al registrar personal con codificación: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar personal con codificación: {str(e)}"
        )


# -------------------------------------------------
#   LOGIN
# -------------------------------------------------
@router.post("/login", response_model=LoginResponseDTO)
async def login(data: LoginRequestDTO):
    """
    Autentica a un personal y retorna un token de acceso junto con sus datos personales.
    
    - **email**: Correo electrónico del personal
    - **password**: Contraseña del personal (mínimo 8 caracteres)
    
    **Respuesta:**
    - **access_token**: Token JWT para autenticación en endpoints protegidos
    - **token_type**: Tipo de token (siempre "bearer")
    - **personal**: Datos personales del usuario autenticado (id, dni, nombres, email, etc.)
    
    Si las credenciales son inválidas, retorna error 401.
    """
    auth_result = await PersonalService.authenticate(str(data.email), data.password)

    if not auth_result:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return LoginResponseDTO(
        access_token=auth_result["access_token"],
        personal=PersonalResponseDTO.model_validate(auth_result["personal"]),
    )


# -------------------------------------------------
#   LISTAR PERSONAL
# -------------------------------------------------
@router.get("/", response_model=list[PersonalResponseDTO])
async def listar_personal():
    """
    Obtiene una lista de todo el personal registrado en el sistema.
    
    Retorna un array con los datos de cada personal, excluyendo información sensible
    como contraseñas. Cada elemento incluye:
    - id, dni, nombre, apellido_paterno, apellido_materno
    - email, es_administrador, codificacion_facial
    """
    result = await PersonalService.list_all()

    # Evitar que Supabase devuelva password_hash
    cleaned = [
        {k: row[k] for k in (
            "id", "dni", "nombre", "apellido_paterno", "apellido_materno",
            "email", "es_administrador", "codificacion_facial"
        ) if k in row}
        for row in result
    ]

    return cleaned


# -------------------------------------------------
#   OBTENER POR ID
# -------------------------------------------------
@router.get("/{personal_id}", response_model=PersonalResponseDTO)
async def obtener_por_id(personal_id: UUID):
    """
    Obtiene los datos de un personal específico por su ID.
    
    - **personal_id**: UUID del personal a consultar
    
    Retorna los datos completos del personal (sin información sensible).
    Si el personal no existe, retorna error 404.
    """
    result = await PersonalService.get_by_id(personal_id)

    if not result:
        raise HTTPException(status_code=404, detail="Personal no encontrado")

    return result


# -------------------------------------------------
#   ELIMINAR
# -------------------------------------------------
@router.delete("/{personal_id}")
async def eliminar_personal(personal_id: UUID):
    """
    Elimina un personal del sistema por su ID.
    
    - **personal_id**: UUID del personal a eliminar
    
    **Advertencia:** Esta operación es irreversible. Se recomienda verificar
    dependencias (como codificaciones faciales o asistencias) antes de eliminar.
    """
    await PersonalService.delete(personal_id)
    return {"message": "Personal eliminado correctamente"}


# -------------------------------------------------
#   ACTUALIZAR PERSONAL
# -------------------------------------------------
@router.patch("/{personal_id}", response_model=PersonalResponseDTO)
async def actualizar_personal(personal_id: UUID, data: PersonalUpdateDTO):
    """
    Actualiza datos de un personal existente mediante actualización parcial (PATCH).
    
    - **personal_id**: UUID del personal a actualizar
    
    **Campos actualizables (todos opcionales):**
    - dni, nombre, apellido_paterno, apellido_materno
    - email, es_administrador
    - password (se hashea automáticamente si se proporciona)
    
    Solo se actualizan los campos que se envíen en el body. Si el personal no existe,
    retorna error 404.
    """
    actualizado = await PersonalService.update(personal_id, data)

    if not actualizado:
        raise HTTPException(status_code=404, detail="Personal no encontrado")

    return PersonalResponseDTO.model_validate(actualizado)


# -------------------------------------------------
#   RECUPERAR CONTRASEÑA (REQUEST TOKEN)
# -------------------------------------------------
@router.post("/forgot-password")
async def forgot_password(data: RecoverRequestDTO, background_tasks: BackgroundTasks):
    """
    Solicita la recuperación de contraseña mediante envío de email.
    
    - **email**: Correo electrónico del personal que solicita la recuperación
    - **base_url**: URL base de la aplicación (para generar el link de reset)
    
    Genera un token temporal de recuperación y envía un correo electrónico con
    las instrucciones. El token expira en 60 minutos.
    
    **Nota:** Por seguridad, siempre retorna el mismo mensaje independientemente
    de si el email existe o no, para evitar enumeración de usuarios.
    """
    # Ejecutar en background para no bloquear el request
    background_tasks.add_task(
        PersonalService.create_password_reset,
        str(data.email),
        data.base_url
    )

    # Misma respuesta siempre → evita revelar si el email existe
    return {"message": "Si el email existe, recibirás instrucciones para recuperar la contraseña."}


# -------------------------------------------------
#   RESET PASSWORD (USANDO TOKEN)
# -------------------------------------------------
@router.post("/reset/{token}")
async def reset_password(token: str, data: ResetPasswordDTO):
    """
    Restablece la contraseña usando un token de recuperación válido.
    
    - **token**: Token de recuperación recibido por email
    - **password**: Nueva contraseña (mínimo 8 caracteres)
    
    El token debe ser válido y no haber expirado (60 minutos desde su generación).
    Si el token es inválido o expirado, retorna error 400.
    """
    ok = await PersonalService.reset_password(token, data.password)

    if not ok:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    return {"message": "Contraseña restablecida correctamente"}

