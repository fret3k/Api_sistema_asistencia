from fastapi import APIRouter, HTTPException, Body
from typing import List
from uuid import UUID
from schemas.solicitudes_ausencias_schema import SolicitudAusenciaSchema, SolicitudAusenciaCreate, SolicitudAusenciaUpdate
from repository.solicitudes_ausencias_repository import SolicitudesAusenciasRepository
from repository.personal_repository import PersonalRepository
from datetime import datetime

router = APIRouter(prefix="/solicitudes-ausencias", tags=["Solicitudes Ausencias"])

@router.get("/", response_model=List[SolicitudAusenciaSchema])
async def get_all_solicitudes():
    return await SolicitudesAusenciasRepository.find_all()

@router.get("/personal/{personal_id}", response_model=List[SolicitudAusenciaSchema])
async def get_solicitudes_by_personal(personal_id: UUID):
    return await SolicitudesAusenciasRepository.find_by_personal(personal_id)

@router.post("/", response_model=SolicitudAusenciaSchema)
async def create_solicitud(solicitud: SolicitudAusenciaCreate):
    # Validar que el personal existe (opcional pero recomendado)
    # personal = await PersonalRepository.find_by_id(solicitud.personal_id)
    # if not personal:
    #    raise HTTPException(status_code=404, detail="Personal no encontrado")

    data = solicitud.dict()
    # Convert dates/times to ISO strings for Supabase if needed, but python client handles it mostly.
    # Supabase expects strings for UUIDs usually, but the driver might handle it.
    # Explicit conversion to be safe:
    data['personal_id'] = str(data['personal_id'])
    data['tipo_ausencia'] = data['tipo_ausencia'].upper()
    data['estado_solicitud'] = "PENDIENTE"
    
    # Dates to string
    data['fecha_inicio'] = data['fecha_inicio'].isoformat()
    data['fecha_fin'] = data['fecha_fin'].isoformat()
    if data['hora_inicio']:
         data['hora_inicio'] = data['hora_inicio'].isoformat()
    if data['hora_fin']:
         data['hora_fin'] = data['hora_fin'].isoformat()

    new_solicitud = await SolicitudesAusenciasRepository.create(data)
    if not new_solicitud:
        raise HTTPException(status_code=500, detail="Error al crear la solicitud")
    return new_solicitud

@router.patch("/{id}/estado", response_model=SolicitudAusenciaSchema)
async def update_solicitud_status(id: UUID, estado_update: SolicitudAusenciaUpdate):
    estado = estado_update.estado_solicitud.upper()
    valid_statuses = ['PENDIENTE', 'APROBADA', 'DENEGADA', 'ANULADA']
    if estado not in valid_statuses:
         raise HTTPException(status_code=400, detail="Estado inválido")
         
    updated = await SolicitudesAusenciasRepository.update_estado(id, estado)
    if not updated:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return updated
