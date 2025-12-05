from config.supabaseClient import get_supabase
from uuid import UUID
from typing import Any, Union

class EncodingFaceRepository:
    table = "codificacion_facial"

    @staticmethod
    async def create(data: dict[str, Any]):
        """
        Crea una nueva codificación facial en la base de datos.
        Asegura que los UUIDs se conviertan a strings y el embedding sea un array válido.
        """
        supabase = get_supabase()
        
        # Preparar payload asegurando tipos correctos
        payload = {}
        
        # Convertir personal_id a string si es UUID
        if "personal_id" in data:
            personal_id = data["personal_id"]
            if isinstance(personal_id, UUID):
                payload["personal_id"] = str(personal_id)
            else:
                payload["personal_id"] = personal_id
        
        # Asegurar que embedding sea una lista de floats
        if "embedding" in data:
            embedding = data["embedding"]
            if isinstance(embedding, list):
                # Convertir todos a float y asegurar que sean 128 valores
                payload["embedding"] = [float(x) for x in embedding]
            else:
                payload["embedding"] = embedding
        
        result = supabase.table(EncodingFaceRepository.table).insert(payload).execute()
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
