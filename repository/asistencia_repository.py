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

    @staticmethod
    async def obtener_historial(fecha: date = None, personal_id: str = None):
        query = get_supabase().table("asistencias").select("*, personal(*)")
        
        if fecha:
            query = query.eq("fecha", fecha.isoformat())
        
        if personal_id:
            query = query.eq("personal_id", personal_id)
            
        # Ordenar por fecha y hora descendente
        result = query.order("marca_tiempo", desc=True).execute()
        return result.data if result.data else []

    @staticmethod
    async def obtener_registros_por_rango(fecha_inicio: date, fecha_fin: date, personal_id: str = None):
        query = get_supabase().table("asistencias").select("*, personal(*)") \
            .gte("fecha", fecha_inicio.isoformat()) \
            .lte("fecha", fecha_fin.isoformat())

        if personal_id:
            query = query.eq("personal_id", personal_id)

        result = query.order("marca_tiempo", desc=True).execute()
        return result.data if result.data else []
