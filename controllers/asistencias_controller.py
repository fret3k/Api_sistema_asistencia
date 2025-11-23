from fastapi import APIRouter
from dto.asistencia_dto.asistencia_dto import RegistrarAsistenciaDTO
from services.asistencias_service import AsistenciaService

router = APIRouter(prefix="/asistencia")
service = AsistenciaService()

@router.post("/registrar")
async def registrar_asistencia(dto: RegistrarAsistenciaDTO):
    return await service.registrar_asistencia(dto)

