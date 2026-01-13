from datetime import datetime, date, time
from config.config_horarios import HORARIOS
from config.timezone_config import LOCAL_TIMEZONE
from repository.asistencia_repository import AsistenciaRepository
from repository.personal_repository import PersonalRepository
from repository.encoding_face_repository import EncodingFaceRepository
import math
from dto.asistencia_dto.realtime_asistencia_dto import RealtimeAsistenciaDTO
from uuid import UUID


class AsistenciaService:

    def evaluar_estado(self, tipo_registro: str, hora_actual: time):
        """
        Evalúa el estado de la asistencia según el turno
        """
        if tipo_registro == "MAÑANA":
            cfg = HORARIOS.get("ENTRADA_M")
            if not cfg:
                return "NORMAL"
            if hora_actual <= cfg["a_tiempo"]:
                return "A TIEMPO"
            return "TARDE"
        
        elif tipo_registro == "TARDE":
            cfg = HORARIOS.get("ENTRADA_T")
            if not cfg:
                return "NORMAL"
            if hora_actual <= cfg["a_tiempo"]:
                return "A TIEMPO"
            return "TARDE"

        return "NORMAL"

    def determinar_tipo_registro(self, hora_actual: time):
        """
        Simplificado: Solo registra un turno (MAÑANA o TARDE)
        Ya no distingue entre entrada y salida
        """
        # Límite entre turno mañana y tarde (aproximadamente mediodía/inicio tarde)
        inicio_turno_tarde = HORARIOS["ENTRADA_T"].get("inicio_marcacion", time(14, 0))
        
        # Si es antes de las 14:00, es turno mañana
        if hora_actual < inicio_turno_tarde:
            return "MAÑANA"
        else:
            return "TARDE"

    async def registrar_asistencia(self, dto):

        # Si viene de reconocimiento facial, ya se validó antes
        if hasattr(dto, 'reconocimiento_valido') and not dto.reconocimiento_valido:
             return {"error": "El rostro no coincide con el usuario"}
             
        # Si NO viene validado (manual), asumimos que lo valida el frontend o middleware de auth
        # (Idealmente, validar permisos de admin aquí si es manual)

        personal = await PersonalRepository.find_by_id(dto.personal_id)

        if not personal:
            return {"error": "Usuario no encontrado"}

        # Usar la zona horaria local configurada (UTC-5)
        if hasattr(dto, 'marca_tiempo') and dto.marca_tiempo:
            # Asegurarse de que el datetime sea consciente de la zona horaria local
            ahora = dto.marca_tiempo
            if ahora.tzinfo is None:
                ahora = ahora.replace(tzinfo=LOCAL_TIMEZONE)
            else:
                ahora = ahora.astimezone(LOCAL_TIMEZONE)
        else:
            ahora = datetime.now(LOCAL_TIMEZONE)

        hoy = ahora.date()
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
                
                # Mensajes amigables para usuarios
                turno_texto = "turno de la mañana" if tipo_registro == "MAÑANA" else "turno de la tarde"
                hora_registro = r["marca_tiempo"].split("T")[1].split(".")[0][:5] if "T" in str(r["marca_tiempo"]) else "N/A"
                
                return {
                    "ya_registrado": True,
                    "mensaje": f"✓ Ya registrado ({tipo_registro})",
                    "detalle": f"Marcado a las {hora_registro}",
                    "usuario": usuario_nombre,
                    "turno": turno_texto,
                    "estado": r["estado"],
                    "hora": hora_registro,
                }

        # Registrar en la tabla con timestamp explícito en zona horaria local
        data = {
            "personal_id": str(dto.personal_id),
            "fecha": hoy.isoformat(),
            "marca_tiempo": ahora.isoformat(),  # Timestamp con zona horaria local
            "tipo_registro": tipo_registro,
            "estado": estado,
            "motivo": dto.motivo if hasattr(dto, "motivo") else None
        }

        await AsistenciaRepository.registrar_asistencia(data)

        usuario_nombre = personal.get("nombre_completo") or " ".join(filter(None, [personal.get("nombre"), personal.get("apellido_paterno"), personal.get("apellido_materno")]))

        # Mensajes amigables según el estado
        turno_texto = "turno de la mañana" if tipo_registro == "MAÑANA" else "turno de la tarde"
        hora_registro = hora_actual.strftime("%H:%M")
        
        if estado == "A TIEMPO":
            mensaje = f"✓ Registrado - {tipo_registro}"
            detalle = f"A tiempo ({hora_registro})"
        elif estado == "TARDE":
            mensaje = f"⚠ Registrado - {tipo_registro}"
            detalle = f"Tarde ({hora_registro})"
        else:
            mensaje = f"✓ Registrado - {tipo_registro}"
            detalle = f"Hora: {hora_registro}"

        return {
            "exito": True,
            "mensaje": mensaje,
            "detalle": detalle,
            "usuario": usuario_nombre,
            "turno": turno_texto,
            "estado": estado,
            "hora": hora_registro,
        }

    async def listar_personal_status(self, fecha: date = None):
        if not fecha:
            fecha = datetime.now(LOCAL_TIMEZONE).date()

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
            
            # Calcular estado del día (Presente si tiene al menos un registro)
            estado_dia = "PRESENTE" if regs else "AUSENTE"
            
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

    async def obtener_asistencias_recientes(self, limite: int = 5):
        """
        Obtiene las últimas asistencias registradas y estadísticas generales
        """
        from repository.asistencia_repository import AsistenciaRepository
        
        try:
            # Obtener asistencias recientes ordenadas por fecha y hora
            registros = await AsistenciaRepository.obtener_recientes(limite)
            
            # Obtener estadísticas del día para el panel
            stats_raw = await self.obtener_estadisticas_dia(datetime.now(LOCAL_TIMEZONE).date())
            
            # Formatear para el frontend
            lista_recientes = []
            for r in registros:
                # Extraer datos del personal
                personal = r.get("personal") or {}
                nombre = personal.get("nombre_completo") if isinstance(personal, dict) else "Usuario"
                
                # Si no hay nombre_completo, construirlo
                if not nombre or nombre == "Usuario":
                    nombre = " ".join(filter(None, [
                        personal.get("nombre", ""),
                        personal.get("apellido_paterno", ""),
                        personal.get("apellido_materno", "")
                    ])) if isinstance(personal, dict) else "Usuario"
                
                # Formatear turno
                tipo_registro = r.get("tipo_registro", "")
                turno_texto = "Turno Mañana" if "MAÑANA" in tipo_registro else "Turno Tarde"
                
                # Formatear hora y fecha en zona horaria local
                marca_tiempo_raw = r.get("marca_tiempo", "")
                try:
                    # Supabase devuelve UTC, convertimos a local
                    dt_utc = datetime.fromisoformat(str(marca_tiempo_raw).replace('Z', '+00:00'))
                    dt_local = dt_utc.astimezone(LOCAL_TIMEZONE)
                    hora = dt_local.strftime("%H:%M:%S")
                    fecha = dt_local.strftime("%d/%m")
                except Exception as e:
                    print(f"Error formateando fecha: {e}")
                    hora = str(marca_tiempo_raw).split("T")[1].split(".")[0] if "T" in str(marca_tiempo_raw) else "N/A"
                    fecha = str(r.get("fecha", ""))

                lista_recientes.append({
                    "id": r.get("id"),
                    "usuario": nombre,
                    "turno": turno_texto,
                    "estado": r.get("estado", "NORMAL"),
                    "hora": hora,
                    "fecha": fecha
                })
            
            return {
                "asistencias": lista_recientes,
                "estadisticas": {
                    "presentes": stats_raw.get("presentes", 0),
                    "tardanzas": stats_raw.get("tardanzas", 0),
                    "faltas": stats_raw.get("ausentes", 0),
                    "total": stats_raw.get("total_personal", 0)
                }
            }
        except Exception as e:
            print(f"Error en obtener_asistencias_recientes: {e}")
            return {"asistencias": [], "estadisticas": {"presentes": 0, "tardanzas": 0, "faltas": 0, "total": 0}}


    # ----------------- Nuevo: procesar embeddings en tiempo real ------------------
    async def procesar_realtime(self, dto: RealtimeAsistenciaDTO):
        # Configuración de validación de identidad
        # Usar valores del frontend si vienen, sino usar valores por defecto
        THRESHOLD = getattr(dto, 'threshold', None) or 0.75
        MIN_MARGIN = getattr(dto, 'min_margin', None) or 0.06

        # Validaciones basicas
        if not dto.embedding or len(dto.embedding) < 64:
            return {"error": "❌ Error al procesar tu rostro. Por favor, intenta de nuevo."}

        # Traer todas las codificaciones faciales con manejo de errores de conexión
        try:
            records = await EncodingFaceRepository.find_all()
        except Exception as e:
            # Manejar errores de conexión a la base de datos
            error_msg = str(e).lower()
            if "timeout" in error_msg or "connect" in error_msg:
                return {"error": "⚠ No se puede conectar al sistema. Por favor, intenta de nuevo."}
            return {"error": "⚠ Error del sistema. Contacta al administrador."}
        
        if not records:
            return {"error": "❌ No hay usuarios registrados en el sistema."}

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

        # Log para auditoría (solo para consola del servidor)
        print(f"[ASISTENCIA] Score: {best_score:.4f}, Segundo: {second_best_score:.4f}, Threshold: {THRESHOLD}")

        # Validar threshold mínimo de similitud
        if best_score < THRESHOLD:
            print(f"[ASISTENCIA] RECHAZADO - Score {best_score:.4f} < Threshold {THRESHOLD}")
            return {"error": "❌ No se pudo identificar tu rostro. Asegúrate de estar bien iluminado e intenta de nuevo."}

        # Validar margen de confianza (evitar matches ambiguos)
        margin = best_score - second_best_score
        
        # Ajustar margen dinámicamente: Si el score es muy alto, el margen puede ser menor
        ajuste_margen = MIN_MARGIN
        if best_score > 0.92:
            ajuste_margen = MIN_MARGIN * 0.5  # Si es > 92%, reducir exigencia de margen a la mitad
        
        if second_best_score > 0 and margin < ajuste_margen:
            print(f"[ASISTENCIA] RECHAZADO - Margen {margin:.4f} < Ajustado {ajuste_margen:.4f} (Mínimo original {MIN_MARGIN})")
            return {"error": "⚠ No se pudo verificar tu identidad con certeza (Match ambiguo). Por favor, intenta de nuevo."}
        
        print(f"[ASISTENCIA] APROBADO - Score {best_score:.4f}, Margen {margin:.4f}")

        personal_id = best.get("personal_id")

        # verificar que el personal exista en la tabla personal
        personal = await PersonalRepository.find_by_id(personal_id)
        if not personal:
            return {"error": "❌ Usuario no encontrado en el sistema."}

        # construir un dto simplificado para reutilizar registrar_asistencia
        class _TmpDTO:
            pass

        tmp = _TmpDTO()
        tmp.reconocimiento_valido = True
        tmp.personal_id = personal_id
        tmp.motivo = getattr(dto, "motivo", None)
        tmp.marca_tiempo = getattr(dto, "marca_tiempo", None)

        # Si solo se requiere validar identidad (para mostrar modal de confirmación)
        if getattr(dto, "solo_validar", False):
            # Determinar qué turno y estado le correspondería
            ahora = datetime.now(LOCAL_TIMEZONE)
            if dto.marca_tiempo:
                ahora = dto.marca_tiempo.astimezone(LOCAL_TIMEZONE) if dto.marca_tiempo.tzinfo else dto.marca_tiempo.replace(tzinfo=LOCAL_TIMEZONE)
            
            tipo_registro = self.determinar_tipo_registro(ahora.time())
        # Si solo se requiere validar identidad (para mostrar modal de confirmación)
        if getattr(dto, "solo_validar", False):
            # Determinar qué turno y estado le correspondería
            ahora = datetime.now(LOCAL_TIMEZONE)
            if dto.marca_tiempo:
                ahora = dto.marca_tiempo.astimezone(LOCAL_TIMEZONE) if dto.marca_tiempo.tzinfo else dto.marca_tiempo.replace(tzinfo=LOCAL_TIMEZONE)
            
            tipo_registro = self.determinar_tipo_registro(ahora.time())
            estado = self.evaluar_estado(tipo_registro, ahora.time())
            turno_texto = "turno de la mañana" if tipo_registro == "MAÑANA" else "turno de la tarde"
            
            # Verificar si ya existe registro hoy
            hoy = ahora.date()
            registros = await AsistenciaRepository.obtener_registros_del_dia(
                str(personal_id), hoy
            )
            
            ya_registrado = False
            mensaje_ya_registrado = None
            hora_ya_registrada = None
            
            for r in registros:
                if r["tipo_registro"] == tipo_registro:
                    ya_registrado = True
                    hora_ya_registrada = r["marca_tiempo"].split("T")[1].split(".")[0][:5] if "T" in str(r["marca_tiempo"]) else "N/A"
                    mensaje_ya_registrado = f"✓ Ya registrado ({tipo_registro}) a las {hora_ya_registrada}"
                    break
            
            return {
                "reconocido": True,
                "personal_id": personal_id,
                "usuario": personal.get("nombre_completo") or f"{personal.get('nombre')} {personal.get('apellido_paterno')}",
                "turno": turno_texto,
                "tipo_registro": tipo_registro,
                "estado": estado,
                "hora": ahora.strftime("%H:%M:%S"),
                "preview": True,
                "ya_registrado": ya_registrado,
                "mensaje": mensaje_ya_registrado if ya_registrado else None
            }

        # Reutilizar el método registrar_asistencia que ya incluye:
        # - Validación de reconocimiento
        # - Verificación de usuario existente
        # - Verificación de registro duplicado del mismo tipo hoy
        # - Determinación automática de tipo y estado
        asistencia_result = await self.registrar_asistencia(tmp)

        # Si registrar_asistencia devolvió un error, propagarlo
        if isinstance(asistencia_result, dict) and asistencia_result.get("error"):
            return asistencia_result

        usuario_nombre = personal.get("nombre_completo") or " ".join(filter(None, [personal.get("nombre"), personal.get("apellido_paterno")]))

        # Devolver la información completa sin exponer datos técnicos
        return {
            **asistencia_result,  # Incluye mensaje, detalle, usuario, turno, estado, hora
            "reconocido": True,
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
