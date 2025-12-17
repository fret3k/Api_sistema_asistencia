from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Query
from dto.asistencia_dto.asistencia_dto import RegistrarAsistenciaDTO
from dto.asistencia_dto.realtime_asistencia_dto import RealtimeAsistenciaDTO
from services.asistencias_service import AsistenciaService
from datetime import date
from typing import Optional

router = APIRouter(prefix="/asistencia" , tags=["Asistencias"])
service = AsistenciaService()

# simple websocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()


@router.get("/personal")
async def get_personal_status(fecha: Optional[date] = None):
    return await service.listar_personal_status(fecha)

@router.get("/historial")
async def get_historial(
    fecha_inicio: date, 
    fecha_fin: date, 
    personal_id: Optional[str] = None
):
    return await service.obtener_historial_completo(fecha_inicio, fecha_fin, personal_id)

@router.get("/estadisticas")
async def get_estadisticas(fecha: Optional[date] = None):
    if not fecha:
        fecha = date.today()
    return await service.obtener_estadisticas_dia(fecha)

@router.post("/registrar")
async def registrar_asistencia(dto: RegistrarAsistenciaDTO):
    # DTO needs to support manual entry fields if not already
    result = await service.registrar_asistencia(dto)
    
    if isinstance(result, dict) and result.get("error"):
         raise HTTPException(status_code=400, detail=result.get("error"))

    # Notificar WS
    await manager.broadcast({"evento": "asistencia_registrada", "data": result})
    return result


@router.post("/realtime")
async def registrar_realtime(dto: RealtimeAsistenciaDTO):
    # procesa embedding, busca match y registra la asistencia
    result = await service.procesar_realtime(dto)

    # Manejo de errores retornados por el servicio
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno")

    if isinstance(result, dict) and result.get("error"):
        # devolver 400 con detalle para que frontend/Postman lo muestre
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error"))

    # Normalizar respuesta: extraer usuario y campos principales
    asistencia = result.get("asistencia") if isinstance(result, dict) else None
    score = result.get("score") if isinstance(result, dict) else None
    matched_id = result.get("matched_personal_id") if isinstance(result, dict) else None

    resp = {"score": score, "matched_personal_id": matched_id}

    if isinstance(asistencia, dict):
        # Si el servicio devolvió la estructura de registrar_asistencia
        resp.update({
            "mensaje": asistencia.get("mensaje"),
            "usuario": asistencia.get("usuario"),
            "tipo": asistencia.get("tipo"),
            "estado": asistencia.get("estado"),
            "fecha": asistencia.get("fecha"),
        })

    # Notificar a clientes websocket conectados que hubo una nueva asistencia
    if not isinstance(result, dict) or (isinstance(result, dict) and result.get("asistencia")):
        await manager.broadcast({"evento": "asistencia_registrada", "data": resp})

    return resp


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # esperar mensajes del cliente (ping/pong o suscripción opcional)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
