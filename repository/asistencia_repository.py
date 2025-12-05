from datetime import date

from config.supabaseClient import get_supabase

class AsistenciaRepository:

    @staticmethod
    async def obtener_registros_del_dia(personal_id: str, fecha: date):
        result = get_supabase().table("asistencias") \
            .select("*") \
            .eq("personal_id", str(personal_id)) \
            .eq("fecha", fecha.isoformat()) \
            .execute()

        return result.data if result.data else []

    @staticmethod
    async def registrar_asistencia(data: dict):
        result = get_supabase().table("asistencias") \
            .insert(data) \
            .execute()
        return result.data[0] if result.data else None
