from fastapi import APIRouter, HTTPException
from uuid import UUID

from dto.codificacion_facial_dto.endodig_face_request_dto import EncodingFaceCreateDTO
from dto.codificacion_facial_dto.encodig_face_response_dto import EncodingFaceResponseDTO
from services.encoding_face_service import EncodingFaceService

router = APIRouter(prefix="/encoding-face", tags=["Encoding Face"])


@router.post("/", response_model=EncodingFaceResponseDTO, status_code=201)
async def crear_codificacion_facial(data: EncodingFaceCreateDTO):
    """
    Crea una nueva codificación facial para un personal existente.
    
    - **personal_id**: UUID del personal al que pertenece la codificación
    - **embedding**: Array de números flotantes que representa el embedding facial
      (vector de 128 valores para modelos estándar como face_recognition)
    
    **Nota:** El personal debe existir previamente en el sistema. Un personal puede tener
    múltiples codificaciones faciales (útil para diferentes ángulos o condiciones de iluminación).
    """
    result = await EncodingFaceService.create(data)

    if not result:
        raise HTTPException(status_code=400, detail="No se pudo crear la codificación facial")

    return EncodingFaceResponseDTO.model_validate(result)


@router.get("/", response_model=list[EncodingFaceResponseDTO])
async def listar():
    """
    Obtiene una lista de todas las codificaciones faciales registradas en el sistema.
    
    Retorna un array con todas las codificaciones, incluyendo:
    - id, personal_id, embedding
    """
    result = await EncodingFaceService.list_all()
    return result


@router.get("/{id}", response_model=EncodingFaceResponseDTO)
async def obtener_por_id(id: UUID):
    """
    Obtiene una codificación facial específica por su ID.
    
    - **id**: UUID de la codificación facial a consultar
    
    Retorna los datos completos de la codificación facial. Si no existe, retorna error 404.
    """
    result = await EncodingFaceService.get_by_id(id)
    if not result:
        raise HTTPException(status_code=404, detail="Codificación facial no encontrada")
    return result


@router.get("/personal/{personal_id}", response_model=list[EncodingFaceResponseDTO])
async def obtener_por_personal(personal_id: UUID):
    """
    Obtiene todas las codificaciones faciales asociadas a un personal específico.
    
    - **personal_id**: UUID del personal
    
    Retorna un array con todas las codificaciones faciales del personal.
    Útil para obtener todos los embeddings de un usuario para comparación en reconocimiento facial.
    """
    result = await EncodingFaceService.find_by_personal(personal_id)
    return result


@router.delete("/{id}")
async def eliminar(id: UUID):
    """
    Elimina una codificación facial del sistema por su ID.
    
    - **id**: UUID de la codificación facial a eliminar
    
    **Advertencia:** Esta operación es irreversible. Al eliminar una codificación,
    el personal perderá esa referencia facial para reconocimiento.
    """
    await EncodingFaceService.delete(id)
    return {"message": "Codificación facial eliminada correctamente"}
