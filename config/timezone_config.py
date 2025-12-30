from datetime import timezone, timedelta

# Zona horaria de Colombia/Perú (UTC-5)
TIMEZONE_OFFSET = timedelta(hours=-5)
LOCAL_TIMEZONE = timezone(TIMEZONE_OFFSET)

def get_local_timezone():
    """Retorna la zona horaria local configurada para el sistema"""
    return LOCAL_TIMEZONE
