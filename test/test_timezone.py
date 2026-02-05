"""
Script de prueba para verificar que la zona horaria está configurada correctamente
"""
from datetime import datetime
from config.timezone_config import LOCAL_TIMEZONE

# Obtener hora actual en zona horaria local
ahora_local = datetime.now(LOCAL_TIMEZONE)
ahora_utc = datetime.utcnow()

print("=" * 60)
print("VERIFICACIÓN DE ZONA HORARIA")
print("=" * 60)
print(f"\n📍 Zona horaria configurada: UTC-5 (Colombia/Perú)")
print(f"\n🕐 Hora UTC (servidor):     {ahora_utc.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🕐 Hora Local (UTC-5):      {ahora_local.strftime('%Y-%m-%d %H:%M:%S %z')}")
print(f"\n📅 Fecha local:             {ahora_local.date()}")
print(f"⏰ Hora local:              {ahora_local.time()}")
print(f"\n💾 Formato ISO (guardado):  {ahora_local.isoformat()}")
print("\n" + "=" * 60)
print("✅ Si la hora local coincide con tu reloj, la configuración es correcta")
print("=" * 60)
