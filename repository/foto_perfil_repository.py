from config.supabaseClient import get_supabase
from uuid import UUID
from typing import Optional

class FotoPerfilRepository:
    table = "fotos_perfil"

    @staticmethod
    async def create_or_update(personal_id: UUID, foto_base64: str):
        supabase = get_supabase()
        # Verificar si ya existe
        existing = supabase.table(FotoPerfilRepository.table).select("id").eq("personal_id", str(personal_id)).execute()
        
        data = {
            "personal_id": str(personal_id),
            "foto_base64": foto_base64
        }
        
        if existing.data:
            result = supabase.table(FotoPerfilRepository.table).update(data).eq("personal_id", str(personal_id)).execute()
        else:
            result = supabase.table(FotoPerfilRepository.table).insert(data).execute()
            
        return result.data[0] if result.data else None

    @staticmethod
    async def find_by_personal_id(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(FotoPerfilRepository.table).select("*").eq("personal_id", str(personal_id)).execute()
        return result.data[0] if result.data else None

    @staticmethod
    async def delete_by_personal_id(personal_id: UUID):
        supabase = get_supabase()
        result = supabase.table(FotoPerfilRepository.table).delete().eq("personal_id", str(personal_id)).execute()
        return result.data
