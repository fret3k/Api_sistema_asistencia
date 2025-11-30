from fastapi import APIRouter, HTTPException, BackgroundTasks
from uuid import UUID

from dto.personal_dto.personal_request_dto import PersonalCreateDTO
from dto.personal_dto.personal_response_dto import PersonalResponseDTO
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


router = APIRouter(prefix="/personal", tags=["Personal"])


@router.post("/", response_model=PersonalResponseDTO, status_code=201)
async def crear_personal(data: PersonalCreateDTO):
    """Crear un nuevo personal. El DTO debe incluir `password` (texto plano); el service lo hashea antes de persistir.

    La respuesta no incluye campos sensibles como `password_hash`.
    """
    result = await PersonalService.create(data)
    if not result:
        raise HTTPException(status_code=400, detail="No se pudo crear el personal")
    # Normalizar/validar salida con el DTO de respuesta para no exponer `password_hash`
    try:
        resp = PersonalResponseDTO.model_validate(result)
    except Exception:
        # si no podemos mapear, devolver el diccionario filtrado manualmente
        filtered = {k: result[k] for k in ("id", "dni", "nombre_completo", "email", "es_administrador", "codificacion_facial") if k in result}
        return filtered
    return resp


@router.post("/login", response_model=TokenResponseDTO)
async def login(data: LoginRequestDTO):
    # convertir EmailStr a str antes de pasarlo al service
    token = await PersonalService.authenticate(str(data.email), data.password)
    if not token:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return TokenResponseDTO(access_token=token)


@router.get("/", response_model=list[PersonalResponseDTO])
async def listar_personal():
    return await PersonalService.list_all()


@router.get("/{personal_id}", response_model=PersonalResponseDTO)
async def obtener_por_id(personal_id: UUID):
    result = await PersonalService.get_by_id(personal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Personal no encontrado")
    return result


@router.delete("/{personal_id}")
async def eliminar_personal(personal_id: UUID):
    await PersonalService.delete(personal_id)
    return {"message": "Personal eliminado correctamente"}


@router.post("/forgot-password")
async def forgot_password(data: RecoverRequestDTO, background_tasks: BackgroundTasks):
    # Lanzar la operación en background para no bloquear la petición
    # pasar email como str para evitar warnings de tipos (EmailStr es un alias)
    background_tasks.add_task(PersonalService.create_password_reset, str(data.email), data.base_url)
    # Responder siempre igual para no filtrar existencia del email
    return {"message": "Si el email existe, recibirás instrucciones para recuperar la contraseña."}


@router.post("/reset/{token}")
async def reset_password(token: str, data: ResetPasswordDTO):
    ok = await PersonalService.reset_password(token, data.password)
    if not ok:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    return {"message": "Contraseña restablecida correctamente"}
