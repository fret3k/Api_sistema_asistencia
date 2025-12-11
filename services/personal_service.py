from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, cast, TypedDict

from repository.personal_repository import PersonalRepository
from dto.personal_dto.personal_request_dto import PersonalCreateDTO
from dto.personal_dto.personal_update_dto import PersonalUpdateDTO
from dto.personal_dto.personal_response_dto import PersonalResponseDTO
from dto.personal_dto.personal_with_encoding_dto import PersonalWithEncodingCreateDTO
from services.encoding_face_service import EncodingFaceService
from dto.codificacion_facial_dto.endodig_face_request_dto import EncodingFaceCreateDTO
from utils.security import hash_password, generate_token, token_expiry, verify_password
from utils.mailer import send_password_reset_email


class AuthResult(TypedDict):
    access_token: str
    personal: dict


class PersonalService:

    @staticmethod
    async def create(data: PersonalCreateDTO):
        """
        Crea un nuevo personal, hasheando la contraseña antes de almacenar.
        Compatible con Pydantic v2 (model_dump).
        """
        payload: dict = data.model_dump()

        # Extraer password del DTO
        password_raw = payload.pop("password", None)

        if password_raw:
            payload["password_hash"] = hash_password(str(password_raw))

        # Guardar en base de datos
        return await PersonalRepository.create(cast(dict, payload))

    @staticmethod
    async def list_all():
        return await PersonalRepository.find_all()

    @staticmethod
    async def get_by_id(personal_id: UUID):
        result = await PersonalRepository.find_by_id(personal_id)
        if not result:
            raise Exception("El personal no existe")
        return result

    @staticmethod
    async def delete(personal_id: UUID):
        return await PersonalRepository.delete(personal_id)

    @staticmethod
    async def update(personal_id: UUID, data: PersonalUpdateDTO):
        """
        Actualiza un personal existente.
        Si viene password, se hashea y se almacena en password_hash.
        """
        payload: dict = data.model_dump(exclude_none=True)

        password_raw = payload.pop("password", None)
        if password_raw:
            payload["password_hash"] = hash_password(str(password_raw))

        return await PersonalRepository.update(personal_id, payload)

    @staticmethod
    async def find_by_email(email: str):
        return await PersonalRepository.find_by_email(email)

    @staticmethod
    async def create_password_reset(email: str, base_url: str) -> bool:
        """
        Genera un token temporal de recuperación de contraseña y envía un correo.
        """
        user = await PersonalRepository.find_by_email(email)

        # No dar pistas si el usuario no existe → evitar enumeración de correos
        if not user:
            return False

        token = generate_token()
        expires = token_expiry(minutes=60)

        # Guardar token en la base de datos
        await PersonalRepository.set_password_reset_token(user["id"], token, expires)

        # Enviar email (debe ejecutarse en background desde el controller)
        send_password_reset_email(user["email"], token, base_url)

        return True

    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool:
        """
        Cambia la contraseña usando un token válido.
        """
        row = await PersonalRepository.find_by_reset_token(token)
        if not row:
            return False

        expires_raw = row.get("password_reset_expires_at")
        if not expires_raw:
            return False

        try:
            expires = datetime.fromisoformat(expires_raw)

            # Asegurar timezone UTC
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)

        except Exception:
            return False

        if expires < datetime.now(timezone.utc):
            return False

        # Hashear nueva contraseña
        password_hash = hash_password(new_password)

        await PersonalRepository.update_password(row["id"], password_hash)

        return True

    @staticmethod
    async def authenticate(email: str, password: str) -> Optional[AuthResult]:
        """
        Autentica a un usuario y retorna un token y los datos personales
        si las credenciales son válidas.
        """
        user = await PersonalRepository.find_by_email(email)

        if not user:
            return None

        hashed = user.get("password_hash")
        if not hashed:
            return None

        try:
            valid = verify_password(password, hashed)
        except Exception:
            return None

        if not valid:
            return None

        # Token simple (no persistido)
        token = generate_token()

        # Normalizar datos públicos del usuario usando el DTO de respuesta
        personal_public = PersonalResponseDTO.model_validate(user).model_dump()

        return AuthResult(access_token=token, personal=personal_public)

    @staticmethod
    async def create_with_encoding(data: PersonalWithEncodingCreateDTO):
        """
        Crea un nuevo personal junto con su codificación facial en una sola operación.
        Primero crea el personal, luego crea la codificación facial asociada.
        
        Returns:
            dict: Contiene personal_id, encoding_id y message
        """
        # Separar datos del personal y del encoding
        personal_data = PersonalCreateDTO(
            dni=data.dni,
            nombre=data.nombre,
            apellido_paterno=data.apellido_paterno,
            apellido_materno=data.apellido_materno,
            email=data.email,
            es_administrador=data.es_administrador,
            password=data.password
        )
        
        # Crear el personal
        personal_result = await PersonalService.create(personal_data)
        
        if not personal_result:
            raise Exception("No se pudo crear el personal")
        
        personal_id = personal_result["id"]
        
        # Crear la codificación facial
        encoding_data = EncodingFaceCreateDTO(
            personal_id=personal_id,
            embedding=data.embedding
        )
        
        encoding_result = await EncodingFaceService.create(encoding_data)
        
        if not encoding_result:
            # Si falla la creación del encoding, podrías eliminar el personal creado
            # Por ahora solo lanzamos excepción
            raise Exception("No se pudo crear la codificación facial")
        
        encoding_id = encoding_result["id"]
        
        return {
            "personal_id": personal_id,
            "encoding_id": encoding_id,
            "message": "Personal y codificación facial registrados correctamente"
        }
