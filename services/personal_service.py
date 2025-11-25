from uuid import UUID
from repository.personal_repository import PersonalRepository
from dto.personal_dto.personal_request_dto import PersonalCreateDTO
from utils.security import hash_password, generate_token, token_expiry
from utils.mailer import send_password_reset_email
from datetime import datetime, timezone
from typing import cast, Optional

class PersonalService:

    @staticmethod
    async def create(data: PersonalCreateDTO):
        # Si viene password en el DTO, hashearla y pasar password_hash al repo
        # usar model_dump() compatible con pydantic v2
        payload: dict = data.model_dump()
        # puede ser None si no se envía password
        from typing import Optional
        # obtener password y convertir a str si existe, si no None
        password_raw = payload.get("password")
        password = str(password_raw) if password_raw is not None else None
        # eliminar la clave password del payload si existe
        if "password" in payload:
            del payload["password"]
        # Asegurar que password sea str no vacío antes de hashear
        if isinstance(password, str) and password:
            payload["password_hash"] = hash_password(password)
        # pasar explícitamente un dict al repositorio para evitar advertencias de tipo
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
    async def find_by_email(email: str):
        return await PersonalRepository.find_by_email(email)

    @staticmethod
    async def create_password_reset(email: str, base_url: str) -> bool:
        user = await PersonalService.find_by_email(email)
        if not user:
            # Para evitar enumeración, no revelar si existe o no
            return False

        token = generate_token()
        expires = token_expiry(minutes=60)
        # persistir token y expiración
        await PersonalRepository.set_password_reset_token(user["id"], token, expires)

        # enviar email (sync) - se recomienda ejecutarlo en background desde el controller
        send_password_reset_email(user["email"], token, base_url)
        return True

    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool:
        row = await PersonalRepository.find_by_reset_token(token)
        if not row:
            return False
        # supabase returns isoformat string for expires
        expires_raw = row.get("password_reset_expires_at")
        if not expires_raw:
            return False
        try:
            # supabase guarda como ISO string sin offset; tratar de parsear y hacer aware
            expires = datetime.fromisoformat(expires_raw)
            if expires.tzinfo is None:
                # asumimos UTC
                expires = expires.replace(tzinfo=timezone.utc)
        except Exception:
            return False

        if expires < datetime.now(timezone.utc):
            return False

        password_hash = hash_password(new_password)
        await PersonalRepository.update_password(row["id"], password_hash)
        return True
