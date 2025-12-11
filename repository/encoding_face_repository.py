from config.supabaseClient import get_supabase
from uuid import UUID
from typing import Any, Union

class EncodingFaceRepository:
    table = "codificacion_facial"

    @staticmethod
    async def create(data: dict[str, Any]):
        supabase = get_supabase()
        result = supabase.table(EncodingFaceRepository.table).insert(data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def find_by_id(id: UUID):
        supabase = get_supabase()
        result = supabase.table(EncodingFaceRepository.table).select("*").eq("id", str(id)).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def find_by_personal_id(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(EncodingFaceRepository.table).select("*").eq("personal_id", str(personal_id)).execute()
        return result.data

    @staticmethod
    async def find_all():
        supabase = get_supabase()
        result = supabase.table(EncodingFaceRepository.table).select("*").execute()
        return result.data

    @staticmethod
    async def delete(id: UUID):
        supabase = get_supabase()
        result = supabase.table(EncodingFaceRepository.table).delete().eq("id", str(id)).execute()
        return result.data
