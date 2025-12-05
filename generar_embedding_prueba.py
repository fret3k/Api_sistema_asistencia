"""
Script para generar un embedding de prueba con 128 valores.
Útil para testing del endpoint de registro de personal con codificación facial.
"""

import random
import json

def generar_embedding_prueba():
    """
    Genera un array de 128 valores flotantes aleatorios entre -1 y 1.
    Simula un embedding facial real.
    """
    return [round(random.uniform(-1.0, 1.0), 6) for _ in range(128)]

def generar_json_ejemplo():
    """
    Genera un JSON completo de ejemplo para el endpoint.
    """
    embedding = generar_embedding_prueba()
    
    ejemplo = {
        "dni": "12345678",
        "nombre": "Juan",
        "apellido_paterno": "Pérez",
        "apellido_materno": "García",
        "email": "juan.perez@example.com",
        "es_administrador": False,
        "password": "MiPassword123",
        "embedding": embedding
    }
    
    return ejemplo

if __name__ == "__main__":
    # Generar ejemplo
    ejemplo = generar_json_ejemplo()
    
    # Mostrar información
    print("=" * 60)
    print("EMBEDDING GENERADO PARA PRUEBAS")
    print("=" * 60)
    print(f"\n✅ Longitud del embedding: {len(ejemplo['embedding'])} valores")
    print(f"✅ Primeros 5 valores: {ejemplo['embedding'][:5]}")
    print(f"✅ Últimos 5 valores: {ejemplo['embedding'][-5:]}")
    
    # Guardar en archivo JSON
    with open("ejemplo_request_completo.json", "w", encoding="utf-8") as f:
        json.dump(ejemplo, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Archivo guardado: ejemplo_request_completo.json")
    print("\n" + "=" * 60)
    print("Puedes usar este JSON directamente en Postman o cURL")
    print("=" * 60)
    
    # Mostrar JSON completo
    print("\n📋 JSON completo:")
    print(json.dumps(ejemplo, indent=2, ensure_ascii=False))

