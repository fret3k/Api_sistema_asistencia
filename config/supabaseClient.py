from supabase import create_client, ClientOptions
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Cliente singleton para reutilizar conexiones
_supabase_client = None

def get_supabase():
    global _supabase_client
    
    if _supabase_client is None:
        # Configurar timeout más largo para evitar errores de conexión
        timeout = httpx.Timeout(
            connect=30.0,   # Tiempo para establecer conexión
            read=30.0,      # Tiempo para leer respuesta
            write=30.0,     # Tiempo para escribir request
            pool=30.0       # Tiempo máximo para obtener conexión del pool
        )
        
        _supabase_client = create_client(
            SUPABASE_URL,
            SUPABASE_KEY,
            options=ClientOptions(
                postgrest_client_timeout=30  # Timeout en segundos
            )
        )
    
    return _supabase_client
