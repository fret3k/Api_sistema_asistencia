from config.supabaseClient import get_supabase
from uuid import UUID

class SolicitudesAusenciasRepository:

    table = "solicitudes_ausencias"

    @staticmethod
    async def create(data: dict):
        supabase = get_supabase()
        result = supabase.table(SolicitudesAusenciasRepository.table).insert(data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def find_by_personal(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(SolicitudesAusenciasRepository.table).select("*").eq("personal_id", str(personal_id)).execute()
        return result.data if result.data else []

    @staticmethod
    async def find_all():
        supabase = get_supabase()
        result = supabase.table(SolicitudesAusenciasRepository.table).select("*").execute()
        return result.data

