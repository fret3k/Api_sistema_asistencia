from datetime import datetime, date, time
from config.config_horarios import HORARIOS
from repository.asistencia_repository import AsistenciaRepository
from repository.personal_repository import PersonalRepository
from repository.encoding_face_repository import EncodingFaceRepository
import math
from dto.asistencia_dto.realtime_asistencia_dto import RealtimeAsistenciaDTO
from uuid import UUID


class AsistenciaService:

    def evaluar_estado(self, tipo_registro: str, hora_actual: time):
        cfg = HORARIOS.get(tipo_registro)
        if not cfg:
            return "OMISION"

        if tipo_registro in ["ENTRADA_M", "ENTRADA_T"]:
            if hora_actual <= cfg["a_tiempo"]:
                return "A TIEMPO"
            elif hora_actual <= cfg["tarde"]:
                return "TARDE"
            # Nuevo: Si pasa de la hora tardía configurada, es inasistencia (FALTA)
            return "FALTA"

        if tipo_registro in ["SALIDA_M", "SALIDA_T"]:
            if hora_actual < cfg["limite_temprano"]:
                return "SALIDA_ANTICIPADA"
            return "A TIEMPO"

        return "OMISION"

    def determinar_tipo_registro(self, hora_actual: time):
        # Usamos los inicios de marcacion para delimitar
        # ENTRADA_M: 07:50 - 12:00
        inicio_em = HORARIOS["ENTRADA_M"].get("inicio_marcacion", time(6,0))
        inicio_sm = HORARIOS["SALIDA_M"].get("inicio_marcacion", time(12,0))
        
        # SALIDA_M: 12:01 - 14:10 (Antes de que permita marcar entrada tarde)
        inicio_et = HORARIOS["ENTRADA_T"].get("inicio_marcacion", time(14,20))
        
        # SALIDA_T: Desde inicio de salida tarde
        inicio_st = HORARIOS["SALIDA_T"].get("inicio_marcacion", time(16,0))

        if inicio_em <= hora_actual < inicio_sm:
            return "ENTRADA_M"
        if inicio_sm <= hora_actual < inicio_et:
            return "SALIDA_M"
        if inicio_et <= hora_actual < inicio_st:
            return "ENTRADA_T"
        if inicio_st <= hora_actual <= time(23, 59):
            return "SALIDA_T"
            
        return "OMISION"

    async def registrar_asistencia(self, dto):

        # Si viene de reconocimiento facial, ya se validó antes
        if hasattr(dto, 'reconocimiento_valido') and not dto.reconocimiento_valido:
             return {"error": "El rostro no coincide con el usuario"}
             
        # Si NO viene validado (manual), asumimos que lo valida el frontend o middleware de auth
        # (Idealmente, validar permisos de admin aquí si es manual)

        personal = await PersonalRepository.find_by_id(dto.personal_id)

        if not personal:
            return {"error": "Usuario no encontrado"}

        hoy = date.today()
        ahora = datetime.now()
        hora_actual = ahora.time()

        # Si el DTO trae tipo_registro forzado (manual), usarlo. Si no, automatico.
        if hasattr(dto, 'tipo_registro') and dto.tipo_registro:
             tipo_registro = dto.tipo_registro
        else:
             tipo_registro = self.determinar_tipo_registro(hora_actual)

        # Si viene estado manual, usarlo? No, calcularlo siempre es mejor para consistencia, 
        # salvo que sea una corrección administrativa.
        # Por ahora calculamos estado basado en hora.
        estado = self.evaluar_estado(tipo_registro, hora_actual)

        # Revisar si ya existe registro del mismo tipo hoy
        registros = await AsistenciaRepository.obtener_registros_del_dia(
            dto.personal_id, hoy
        )

        for r in registros:
            if r["tipo_registro"] == tipo_registro:
                usuario_nombre = personal.get("nombre_completo") or " ".join(filter(None, [personal.get("nombre"), personal.get("apellido_paterno"), personal.get("apellido_materno")]))
                return {
                    "mensaje": "Registro ya realizado",
                    "usuario": usuario_nombre,
                    "tipo": tipo_registro,
                    "estado": r["estado"],
                    "marca_tiempo": r["marca_tiempo"],
                }

        # Registrar en la tabla
        data = {
            "personal_id": str(dto.personal_id),
            "fecha": hoy.isoformat(),
            "tipo_registro": tipo_registro,
            "estado": estado,
            "motivo": dto.motivo if hasattr(dto, "motivo") else None
        }

        await AsistenciaRepository.registrar_asistencia(data)

        usuario_nombre = personal.get("nombre_completo") or " ".join(filter(None, [personal.get("nombre"), personal.get("apellido_paterno"), personal.get("apellido_materno")]))

        return {
            "mensaje": "Asistencia registrada correctamente",
            "usuario": usuario_nombre,
            "tipo": tipo_registro,
            "estado": estado,
            "fecha": hoy.isoformat(),
        }

    async def listar_personal_status(self, fecha: date = None):
        if not fecha:
            fecha = date.today()

        # 1. Obtener todo el personal
        all_personal = await PersonalRepository.find_all()

        # 2. Obtener asistencias del día
        asistencias = await AsistenciaRepository.obtener_historial(fecha=fecha)

        # 3. Mapear asistencias por personal_id
        asistencias_map = {}
        for a in asistencias:
            pid = a["personal_id"]
            if pid not in asistencias_map:
                asistencias_map[pid] = []
            asistencias_map[pid].append(a)

        # 4. Construir resultado
        resultado = []
        for p in all_personal:
            pid = p["id"]
            regs = asistencias_map.get(pid, [])
            
            # Calcular estado del día (Presente si tiene al menos una entrada)
            tiene_entrada = any(r["tipo_registro"] in ["ENTRADA_M", "ENTRADA_T"] for r in regs)
            estado_dia = "PRESENTE" if tiene_entrada else "AUSENTE" # Simplificado
            
            # Ultima marcación
            ultima_marca = None
            if regs:
                # Ya vienen ordenados desc por query
                ultima_marca = regs[0]["marca_tiempo"]
                
            # Calcular horas trabajadas (Aprox)
            # Logica simple: Pares de Entrada/Salida
            horas_trabajadas = 0.0
            # Ordenar ascendente para calculo
            regs_sorted = sorted(regs, key=lambda x: x["marca_tiempo"])
            
            entrada_m = next((r for r in regs_sorted if r["tipo_registro"] == "ENTRADA_M"), None)
            salida_m = next((r for r in regs_sorted if r["tipo_registro"] == "SALIDA_M"), None)
            entrada_t = next((r for r in regs_sorted if r["tipo_registro"] == "ENTRADA_T"), None)
            salida_t = next((r for r in regs_sorted if r["tipo_registro"] == "SALIDA_T"), None)

            def diff_hours(start_str, end_str):
                # Supabase timestamp layout: 2023-10-10T08:00:00+00:00
                if not start_str or not end_str: return 0.0
                try:
                    fmt = "%Y-%m-%dT%H:%M:%S"
                    # A veces trae timezone, a veces no, simplificar
                    t1 = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
                    t2 = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
                    diff = (t2 - t1).total_seconds() / 3600.0
                    return diff if diff > 0 else 0.0
                except:
                    return 0.0

            if entrada_m and salida_m:
                horas_trabajadas += diff_hours(entrada_m["marca_tiempo"], salida_m["marca_tiempo"])
            if entrada_t and salida_t:
                horas_trabajadas += diff_hours(entrada_t["marca_tiempo"], salida_t["marca_tiempo"])

            # Formatear nombre
            nombre_completo = f"{p['nombre']} {p['apellido_paterno']}"
            
            resultado.append({
                "id": pid,
                "dni": p["dni"],
                "nombre_completo": nombre_completo,
                "estado_dia": estado_dia,
                "ultima_marcacion": ultima_marca,
                "horas_trabajadas": round(horas_trabajadas, 2),
                "registros": regs # Detalle si se quiere
            })
            
        return resultado

    async def obtener_historial_completo(self, fecha_inicio: date, fecha_fin: date, personal_id: str = None):
        registros = await AsistenciaRepository.obtener_registros_por_rango(fecha_inicio, fecha_fin, personal_id)
        
        # Formatear respuesta plana para tabla
        datos = []
        for r in registros:
            p = r.get("personal") or {}
            # Si personal es dict (por el join), extraer. Si es None, usar placeholders
            nombre = p.get("nombre", "") if isinstance(p, dict) else ""
            ape = p.get("apellido_paterno", "") if isinstance(p, dict) else ""
            
            datos.append({
                "id": r["id"],
                "personal_id": r["personal_id"],
                "nombre_personal": f"{nombre} {ape}",
                "dni": p.get("dni", "") if isinstance(p, dict) else "",
                "fecha": r["fecha"],
                "marca_tiempo": r["marca_tiempo"],
                "tipo_registro": r["tipo_registro"],
                "estado": r["estado"],
                "motivo": r["motivo"]
            })
        return datos

    async def obtener_estadisticas_dia(self, fecha: date):
        # Reutilizamos logica de status
        status_list = await self.listar_personal_status(fecha)
        
        total = len(status_list)
        presentes = sum(1 for s in status_list if s["estado_dia"] == "PRESENTE")
        ausentes = total - presentes
        
        # Tardanzas: contar cuantos registros tienen estado "TARDE" hoy
        # Podriamos iterar los registros dentro de status_list
        tardanzas = 0
        for s in status_list:
            regs = s["registros"]
            if any(r["estado"] == "TARDE" for r in regs):
                tardanzas += 1

        return {
            "total_personal": total,
            "presentes": presentes,
            "ausentes": ausentes,
            "tardanzas": tardanzas
        }

    # ----------------- Nuevo: procesar embeddings en tiempo real ------------------
    async def procesar_realtime(self, dto: RealtimeAsistenciaDTO):
        # Configuración de validación de identidad
        THRESHOLD = 0.78  # Umbral mínimo de similitud (aumentado para mayor seguridad)
        MIN_MARGIN = 0.1  # Margen mínimo entre mejor y segundo mejor match

        # Validaciones basicas
        if not dto.embedding or len(dto.embedding) < 64:
            return {"error": "Embedding inválido o demasiado corto"}

        # Traer todas las codificaciones faciales con manejo de errores de conexión
        try:
            records = await EncodingFaceRepository.find_all()
        except Exception as e:
            # Manejar errores de conexión a la base de datos
            error_msg = str(e).lower()
            if "timeout" in error_msg or "connect" in error_msg:
                return {"error": "Error de conexión con la base de datos. Por favor, intenta de nuevo."}
            return {"error": f"Error al consultar la base de datos: {str(e)}"}
        
        if not records:
            return {"error": "No hay codificaciones faciales registradas"}

        # Encontrar los 2 mejores matches para validar unicidad
        best = None
        best_score = -1.0
        second_best_score = -1.0
        
        for r in records:
            # r se espera que tenga 'embedding' como lista
            emb = r.get("embedding")
            if not emb:
                continue
            score = self._cosine_similarity(dto.embedding, emb)
            if score > best_score:
                # El mejor actual pasa a ser el segundo mejor
                second_best_score = best_score
                best_score = score
                best = r
            elif score > second_best_score:
                # Actualizar segundo mejor si es mayor
                second_best_score = score

        # Log para auditoría
        print(f"[ASISTENCIA] Score: {best_score:.4f}, Segundo: {second_best_score:.4f}, Threshold: {THRESHOLD}")

        # Validar threshold mínimo de similitud
        if best_score < THRESHOLD:
            print(f"[ASISTENCIA] RECHAZADO - Score {best_score:.4f} < Threshold {THRESHOLD}")
            return {"error": "No se encontró un match confiable", "score": best_score}

        # Validar margen de confianza (evitar matches ambiguos)
        margin = best_score - second_best_score
        if second_best_score > 0 and margin < MIN_MARGIN:
            print(f"[ASISTENCIA] RECHAZADO - Margen {margin:.4f} < Mínimo {MIN_MARGIN} (match ambiguo)")
            return {"error": "Match ambiguo, por favor intente de nuevo", "score": best_score, "margin": margin}
        
        print(f"[ASISTENCIA] APROBADO - Score {best_score:.4f}, Margen {margin:.4f}")

        personal_id = best.get("personal_id")

        # verificar que el personal exista en la tabla personal
        personal = await PersonalRepository.find_by_id(personal_id)
        if not personal:
            return {"error": "Usuario no registrado en la base de datos"}

        # construir un dto simplificado para reutilizar registrar_asistencia
        class _TmpDTO:
            pass

        tmp = _TmpDTO()
        tmp.reconocimiento_valido = True
        tmp.personal_id = personal_id
        tmp.motivo = getattr(dto, "motivo", None)

        # Reutilizar el método registrar_asistencia que ya incluye:
        # - Validación de reconocimiento
        # - Verificación de usuario existente
        # - Verificación de registro duplicado del mismo tipo hoy
        # - Determinación automática de tipo y estado
        asistencia_result = await self.registrar_asistencia(tmp)

        # Si registrar_asistencia devolvió un error, propagarlo
        if isinstance(asistencia_result, dict) and asistencia_result.get("error"):
            return {"error": asistencia_result.get("error"), "score": best_score}

        usuario_nombre = personal.get("nombre_completo") or " ".join(filter(None, [personal.get("nombre"), personal.get("apellido_paterno")]))

        # devolver info junto al score y embedding match
        return {
            "asistencia": asistencia_result,
            "score": best_score,
            "matched_personal_id": personal_id,
            "usuario": usuario_nombre,
        }

    def _cosine_similarity(self, a, b):
        # proteger longitudes diferentes
        n = min(len(a), len(b))
        dot = 0.0
        na = 0.0
        nb = 0.0
        for i in range(n):
            x = float(a[i])
            y = float(b[i])
            dot += x * y
            na += x * x
            nb += y * y
        if na == 0 or nb == 0:
            return 0.0
        return dot / (math.sqrt(na) * math.sqrt(nb))
