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
            return "OMISION"

        if tipo_registro in ["SALIDA_M", "SALIDA_T"]:
            if hora_actual < cfg["limite_temprano"]:
                return "SALIDA_ANTICIPADA"
            return "A TIEMPO"

        return "OMISION"

    def determinar_tipo_registro(self, hora_actual: time):
        if time(6, 0) <= hora_actual <= time(12, 0):
            return "ENTRADA_M"
        if time(12, 1) <= hora_actual <= time(14, 0):
            return "SALIDA_M"
        if time(14, 1) <= hora_actual <= time(18, 0):
            return "ENTRADA_T"
        if time(18, 1) <= hora_actual <= time(23, 59):
            return "SALIDA_T"
        return "OMISION"

    async def registrar_asistencia(self, dto):

        if not dto.reconocimiento_valido:
            return {"error": "El rostro no coincide con el usuario"}

        personal = await PersonalRepository.find_by_id(dto.personal_id)

        if not personal:
            return {"error": "Usuario no encontrado"}

        hoy = date.today()
        ahora = datetime.now()
        hora_actual = ahora.time()

        tipo_registro = self.determinar_tipo_registro(hora_actual)
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

        # Registrar en la tabla EXACTA que definiste
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
