from fastapi import APIRouter, HTTPException
from uuid import UUID

from dto.personal_dto.personal_request_dto import PersonalCreateDTO
from dto.personal_dto.personal_response_dto import PersonalResponseDTO
from services.personal_service import PersonalService

router = APIRouter(prefix="/personal", tags=["Personal"])

@router.post("/", response_model=PersonalResponseDTO)
async def crear_personal(data: PersonalCreateDTO):
    result = await PersonalService.create(data)
    if not result:
        raise HTTPException(status_code=400, detail="No se pudo crear el personal")
    return result

@router.get("/", response_model=list[PersonalResponseDTO])
async def listar_personal():
    return await PersonalService.list_all()

@router.get("/{personal_id}", response_model=PersonalResponseDTO)
async def obtener_por_id(personal_id: UUID):
    result = await PersonalService.get_by_id(personal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Personal no encontrado")
    return result

@router.delete("/{personal_id}")
async def eliminar_personal(personal_id: UUID):
    await PersonalService.delete(personal_id)
    return {"message": "Personal eliminado correctamente"}
