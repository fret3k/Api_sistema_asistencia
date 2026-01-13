from config.supabaseClient import get_supabase
from uuid import UUID

class SolicitudesSobretiempoRepository:

    table = "solicitudes_sobretiempo"

    @staticmethod
    async def create(data: dict):
        supabase = get_supabase()
        result = supabase.table(SolicitudesSobretiempoRepository.table).insert(data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def find_by_personal(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(SolicitudesSobretiempoRepository.table).select("*").eq("personal_id", str(personal_id)).execute()
        return result.data if result.data else []

    @staticmethod
    async def find_all():
        supabase = get_supabase()
        result = supabase.table(SolicitudesSobretiempoRepository.table).select("*").execute()
        return result.data

    @staticmethod
    async def delete_by_personal(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(SolicitudesSobretiempoRepository.table).delete().eq("personal_id", str(personal_id)).execute()
        return result.data
