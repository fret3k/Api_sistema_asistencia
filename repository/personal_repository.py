from config.supabaseClient import get_supabase
from uuid import UUID
from dto.personal_dto.personal_request_dto import PersonalCreateDTO
from dto.personal_dto.personal_update_dto import PersonalUpdateDTO
from typing import Union, Any

class PersonalRepository:

    table = "personal"

    @staticmethod
    async def create(data: Union[PersonalCreateDTO, dict[str, Any]]):
        supabase = get_supabase()
        # `data` puede ser DTO o dict; usar tal cual si ya es dict
        payload = data if isinstance(data, dict) else data.model_dump()
        result = supabase.table(PersonalRepository.table).insert(payload).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def find_all():
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).select("*").execute()
        return result.data

    @staticmethod
    async def find_by_id(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).select("*").eq("id", str(personal_id)).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def delete(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).delete().eq("id", str(personal_id)).execute()
        return result.data

    @staticmethod
    async def update(personal_id: UUID, data: Union[PersonalUpdateDTO, dict[str, Any]]):
        """
        Actualiza un registro de personal por id.
        """
        supabase = get_supabase()
        payload = data if isinstance(data, dict) else data.model_dump(exclude_none=True)
        result = (
            supabase
            .table(PersonalRepository.table)
            .update(payload)
            .eq("id", str(personal_id))
            .execute()
        )
        return result.data[0] if result.data else None

    @staticmethod
    async def find_by_email(email: str):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).select("*").eq("email", email).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def update_password(personal_id: UUID, password_hash: str):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).update({"password_hash": password_hash, "password_reset_token": None, "password_reset_expires_at": None}).eq("id", str(personal_id)).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def set_password_reset_token(personal_id: UUID, token: str, expires_at):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).update({"password_reset_token": token, "password_reset_expires_at": expires_at.isoformat()}).eq("id", str(personal_id)).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def find_by_reset_token(token: str):
        supabase = get_supabase()
        result = supabase.table(PersonalRepository.table).select("*").eq("password_reset_token", token).execute()
        return result.data[0] if result.data else None
