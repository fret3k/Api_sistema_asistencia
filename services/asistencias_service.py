from datetime import datetime, date, time
from config.config_horarios import HORARIOS
from repository.asistencia_repository import AsistenciaRepository
from repository.personal_repository import PersonalRepository


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
                return {
                    "mensaje": "Registro ya realizado",
                    "usuario": personal["nombre_completo"],
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

        return {
            "mensaje": "Asistencia registrada correctamente",
            "usuario": personal["nombre_completo"],
            "tipo": tipo_registro,
            "estado": estado,
            "fecha": hoy.isoformat(),
        }

