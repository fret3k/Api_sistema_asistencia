from fastapi import APIRouter
from dto.horario_dto.horarios_dto import HorariosUpdateDTO
from services.horarios_service import HorariosService

router = APIRouter(prefix="/horarios", tags=["Horarios"])

@router.get("/")
def obtener_horarios():
    """
    Retorna todos los horarios configurados
    """
    return HorariosService.get_horarios()


@router.put("/")
def actualizar_horarios(data: HorariosUpdateDTO):
    """
    Actualiza los horarios enviados desde el frontend
    """
    HorariosService.update_horarios(data.model_dump(exclude_unset=True))
    return {
        "message": "Horarios actualizados correctamente",
        "horarios": HorariosService.get_horarios()
    }
