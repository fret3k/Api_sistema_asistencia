from datetime import date, timedelta
from uuid import UUID
import calendar
from typing import List

from repository.personal_repository import PersonalRepository
from repository.asistencia_repository import AsistenciaRepository
from repository.solicitudes_ausencias_repository import SolicitudesAusenciasRepository
from repository.solicitudes_sobretiempo_repository import SolicitudesSobretiempoRepository
from dto.reporte_dto.reporte_mensual_item_dto import ReporteMensualItemDTO

class ReporteService:

    @staticmethod
    async def generar_reporte_mensual(mes: int, anio: int, personal_id: UUID = None) -> List[ReporteMensualItemDTO]:
        
        # 1. Obtener lista de personal
        if personal_id:
            personal = await PersonalRepository.find_by_id(personal_id)
            lista_personal = [personal] if personal else []
        else:
            lista_personal = await PersonalRepository.find_all()

        reporte = []
        
        # Fechas inicio y fin del mes
        fecha_inicio = date(anio, mes, 1)
        _, last_day = calendar.monthrange(anio, mes)
        fecha_fin = date(anio, mes, last_day)

        # Calcular días laborables (Lunes a Viernes)
        dias_laborables_mes = 0
        current = fecha_inicio
        while current <= fecha_fin:
            if current.weekday() < 5: # 0-4 son Lun-Vie
                dias_laborables_mes += 1
            current += timedelta(days=1)

        # Obtener todas las asistencias del mes (optimizacion: podria hacerse una sola query y filtrar en codigo, 
        # pero por ahora iteramos o consultamos por rango si el repo lo permite.
        # El repo permite obtener por rango y opcional personal_id.
        # Si personal_id es None, trae de todos? Revisemos AsistenciaRepository.obtener_registros_por_rango
        # Si, parece que si.
        
        asistencias_mes = await AsistenciaRepository.obtener_registros_por_rango(fecha_inicio, fecha_fin, str(personal_id) if personal_id else None)
        
        # Obtener solicitudes (traemos todas y filtramos, o mejor, iteramos por persona)
        # Para ser eficientes con la base de datos, lo ideal seria traer todo el rango, pero los repos de solicitudes 
        # actualmente no tienen metodo por rango. Usaremos find_by_personal dentro del loop o find_all y filtramos.
        # Como no voy a modificar los repos de solicitudes ahora, usare find_all o find_by_personal.
        # Para evitar N+1 queries masivos, si son muchos empleados, mejor find_all y filtrar en memoria.
        # Asumiremos trafico moderado y usare find_by_personal por simplicidad y claridad, 
        # ya que find_all de solicitudes podria crecer mucho historicamente.
        # OJO: find_by_personal trae TODO el historial. Si es muy grande, sera lento.
        # TODO: Agregar filtro de fecha a los repos de solicitudes en el futuro.

        numero_correlativo = 1

        for p in lista_personal:
            p_id = str(p['id'])
            
            # Filtrar asistencias de esta persona
            asistencias_p = [a for a in asistencias_mes if a['personal_id'] == p_id]
            
            # Contadores
            dias_asistidos = set()
            tardanzas = 0
            salidas_anticipadas = 0
            
            for a in asistencias_p:
                d_fecha = date.fromisoformat(a['fecha'])
                dias_asistidos.add(d_fecha)
                
                estado = a.get('estado', '')
                if estado == 'TARDE':
                    tardanzas += 1
                elif estado == 'SALIDA_ANTICIPADA': # Verificar si este es el string exacto en BD
                    salidas_anticipadas += 1
            
            # Solicitudes Ausencias
            ausencias = await SolicitudesAusenciasRepository.find_by_personal(p_id)
            dias_ausencia_justificada = 0
            
            for aus in ausencias:
                if aus['estado_solicitud'] == 'APROBADA':
                    # Verificar solapamiento con el mes
                    ai = date.fromisoformat(aus['fecha_inicio'])
                    af = date.fromisoformat(aus['fecha_fin'])
                    
                    # Interseccion de rangos [ai, af] y [fecha_inicio, fecha_fin]
                    rango_inicio = max(ai, fecha_inicio)
                    rango_fin = min(af, fecha_fin)
                    
                    if rango_inicio <= rango_fin:
                        # Contar dias laborables en el rango de ausencia
                        curr = rango_inicio
                        while curr <= rango_fin:
                            if curr.weekday() < 5:
                                dias_ausencia_justificada += 1
                            curr += timedelta(days=1)

            # Solicitudes Sobretiempo
            sobretiempos = await SolicitudesSobretiempoRepository.find_by_personal(p_id)
            horas_sobretiempo = 0.0
            for st in sobretiempos:
                if st['estado_solicitud'] == 'APROBADA':
                    fecha_st = date.fromisoformat(st['fecha_trabajo'])
                    if fecha_inicio <= fecha_st <= fecha_fin:
                        horas_sobretiempo += float(st['horas_solicitadas'])

            # Calculo de Faltas
            # Faltas = Laborables - Asistidos - Ausencias Justificadas
            # OJO: Dias asistidos son dias que fue. Si fue, no es falta.
            # Si tiene ausencia justificada, no es falta.
            # Si es feriado? No estamos considerando feriados aun (segun implementation plan).
            
            # Asegurar no contar doble.
            # Un dia puede ser asistido Y justificado (ej. medio dia)?
            # Regla simple: Si hay registro de asistencia, cuenta como asistido.
            # Si no hay registro, chequeamos si es justificado.
            # Si no es justificado ni asistido, y es laborable, es falta.
            
            # Vamos a iterar los dias laborables del mes para ser precisos
            dias_falta = 0
            
            curr = fecha_inicio
            while curr <= fecha_fin:
                if curr.weekday() < 5: # Es laborable
                    # Fue?
                    if curr in dias_asistidos:
                        pass # Asistio
                    else:
                        # Estaba justificado?
                        justificado = False
                        # Chequear ausencias
                        for aus in ausencias:
                            if aus['estado_solicitud'] == 'APROBADA':
                                ai = date.fromisoformat(aus['fecha_inicio'])
                                af = date.fromisoformat(aus['fecha_fin'])
                                if ai <= curr <= af:
                                    justificado = True
                                    break
                        if not justificado:
                            dias_falta += 1
                curr += timedelta(days=1)


            # Observaciones
            obs = []
            if tardanzas > 2:
                obs.append("Tardanza reiterada")
            if dias_ausencia_justificada > 0:
                obs.append("Ausencia justificada")
            if horas_sobretiempo > 5:
                obs.append("Sobretiempo frecuente")
            
            observaciones_str = ", ".join(obs)

            item = ReporteMensualItemDTO(
                numero=numero_correlativo,
                dni=p.get('dni', ''),
                apellidos_y_nombres=f"{p.get('apellido_paterno', '')} {p.get('apellido_materno', '')} {p.get('nombre', '')}".strip(),
                dias_laborables=dias_laborables_mes,
                dias_asistidos=len(dias_asistidos),
                tardanzas=tardanzas,
                faltas=dias_falta,
                ausencias_justificadas=dias_ausencia_justificada,
                salidas_anticipadas=salidas_anticipadas,
                horas_sobretiempo=horas_sobretiempo,
                observaciones=observaciones_str
            )
            
            reporte.append(item)
            numero_correlativo += 1

        return reporte
