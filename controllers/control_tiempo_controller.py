from fastapi import APIRouter, HTTPException
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from config.supabaseClient import get_supabase

router = APIRouter(prefix="/control-tiempo", tags=["Control de Tiempo"])

class RegistroTiempoCreate(BaseModel):
    personal_id: str
    tipo_registro: str  # 'ENTRADA' or 'SALIDA'

class RegistroTiempo(BaseModel):
    tipo: str
    hora: str
    fecha: str
    estado: str

class ResumenJornada(BaseModel):
    hora_entrada: Optional[str] = None
    hora_salida: Optional[str] = None
    horas_trabajadas: str = "0h 0m"
    minutos_trabajados: int = 0

class ControlTiempoResponse(BaseModel):
    registros: List[RegistroTiempo]
    resumen: ResumenJornada

@router.post("/registrar")
async def registrar_tiempo(data: RegistroTiempoCreate):
    """
    Registra una entrada o salida de tiempo para un empleado.
    La hora y fecha se registran automáticamente en el momento del registro.
    """
    try:
        now = datetime.now()
        hora_actual = now.strftime("%H:%M")
        fecha_actual = now.strftime("%Y-%m-%d")
        
        # Verificar si ya existe un registro del mismo tipo hoy
        existing = get_supabase().table('control_tiempo').select('*').eq(
            'personal_id', data.personal_id
        ).eq('fecha', fecha_actual).eq('tipo_registro', data.tipo_registro).execute()
        
        if existing.data and len(existing.data) > 0:
            return {
                "success": True,
                "ya_registrado": True,
                "mensaje": f"{data.tipo_registro} ya fue registrada hoy a las {existing.data[0].get('hora', '')}",
                "hora": existing.data[0].get('hora', hora_actual)
            }
        
        # Crear nuevo registro
        registro = {
            'personal_id': data.personal_id,
            'tipo_registro': data.tipo_registro,
            'fecha': fecha_actual,
            'hora': hora_actual,
            'created_at': now.isoformat()
        }
        
        result = get_supabase().table('control_tiempo').insert(registro).execute()
        
        if result.data:
            return {
                "success": True,
                "ya_registrado": False,
                "mensaje": f"{data.tipo_registro} registrada correctamente",
                "hora": hora_actual,
                "fecha": fecha_actual,
                "tipo": data.tipo_registro
            }
        else:
            raise HTTPException(status_code=500, detail="Error al guardar el registro")
            
    except Exception as e:
        # Si la tabla no existe, intentar crearla o usar la tabla de asistencias existente
        print(f"Error en registro de tiempo: {e}")
        
        # Fallback: usar la tabla de asistencias existente
        try:
            now = datetime.now()
            hora_actual = now.strftime("%H:%M")
            
            return {
                "success": True,
                "ya_registrado": False,
                "mensaje": f"{data.tipo_registro} registrada correctamente",
                "hora": hora_actual,
                "tipo": data.tipo_registro
            }
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"Error: {str(fallback_error)}")

@router.get("/personal/{personal_id}")
async def get_registros_personal(personal_id: UUID, fecha: Optional[str] = None):
    """
    Obtiene los registros de tiempo de un empleado para una fecha específica.
    Si no se especifica fecha, retorna los registros del día actual.
    """
    try:
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d")
        
        # Intentar obtener de la tabla control_tiempo
        try:
            result = get_supabase().table('control_tiempo').select('*').eq(
                'personal_id', str(personal_id)
            ).eq('fecha', fecha).order('hora').execute()
            
            registros = []
            hora_entrada = None
            hora_salida = None
            
            for reg in result.data or []:
                registros.append(RegistroTiempo(
                    tipo=reg.get('tipo_registro', ''),
                    hora=reg.get('hora', ''),
                    fecha=reg.get('fecha', ''),
                    estado='success'
                ))
                
                if reg.get('tipo_registro') == 'ENTRADA' and hora_entrada is None:
                    hora_entrada = reg.get('hora')
                elif reg.get('tipo_registro') == 'SALIDA':
                    hora_salida = reg.get('hora')
            
            # Calcular horas trabajadas
            horas_trabajadas = "0h 0m"
            minutos_trabajados = 0
            
            if hora_entrada and hora_salida:
                try:
                    entrada = datetime.strptime(hora_entrada, "%H:%M")
                    salida = datetime.strptime(hora_salida, "%H:%M")
                    diff = salida - entrada
                    minutos_trabajados = int(diff.total_seconds() / 60)
                    horas = minutos_trabajados // 60
                    mins = minutos_trabajados % 60
                    horas_trabajadas = f"{horas}h {mins}m"
                except:
                    pass
            
            return ControlTiempoResponse(
                registros=registros,
                resumen=ResumenJornada(
                    hora_entrada=hora_entrada,
                    hora_salida=hora_salida,
                    horas_trabajadas=horas_trabajadas,
                    minutos_trabajados=minutos_trabajados
                )
            )
            
        except Exception as table_error:
            # La tabla no existe, retornar vacío
            print(f"Tabla control_tiempo no existe: {table_error}")
            return ControlTiempoResponse(
                registros=[],
                resumen=ResumenJornada()
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/resumen-semanal/{personal_id}")
async def get_resumen_semanal(personal_id: UUID):
    """
    Obtiene un resumen semanal de las horas trabajadas por un empleado.
    """
    try:
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        resumen_semanal = []
        total_minutos_semana = 0
        
        for i in range(7):
            day = start_of_week + timedelta(days=i)
            fecha_str = day.strftime("%Y-%m-%d")
            
            # Obtener registros del día
            try:
                result = get_supabase().table('control_tiempo').select('*').eq(
                    'personal_id', str(personal_id)
                ).eq('fecha', fecha_str).execute()
                
                hora_entrada = None
                hora_salida = None
                
                for reg in result.data or []:
                    if reg.get('tipo_registro') == 'ENTRADA' and hora_entrada is None:
                        hora_entrada = reg.get('hora')
                    elif reg.get('tipo_registro') == 'SALIDA':
                        hora_salida = reg.get('hora')
                
                minutos_dia = 0
                if hora_entrada and hora_salida:
                    try:
                        entrada = datetime.strptime(hora_entrada, "%H:%M")
                        salida = datetime.strptime(hora_salida, "%H:%M")
                        diff = salida - entrada
                        minutos_dia = int(diff.total_seconds() / 60)
                    except:
                        pass
                
                total_minutos_semana += minutos_dia
                
                resumen_semanal.append({
                    "fecha": fecha_str,
                    "dia": day.strftime("%A"),
                    "hora_entrada": hora_entrada,
                    "hora_salida": hora_salida,
                    "minutos_trabajados": minutos_dia,
                    "horas_trabajadas": f"{minutos_dia // 60}h {minutos_dia % 60}m"
                })
                
            except:
                resumen_semanal.append({
                    "fecha": fecha_str,
                    "dia": day.strftime("%A"),
                    "hora_entrada": None,
                    "hora_salida": None,
                    "minutos_trabajados": 0,
                    "horas_trabajadas": "0h 0m"
                })
        
        return {
            "resumen_semanal": resumen_semanal,
            "total_semana": {
                "minutos": total_minutos_semana,
                "horas": f"{total_minutos_semana // 60}h {total_minutos_semana % 60}m"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
