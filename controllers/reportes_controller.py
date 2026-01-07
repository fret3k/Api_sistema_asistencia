from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from uuid import UUID

from services.reporte_service import ReporteService
from dto.reporte_dto.reporte_mensual_item_dto import ReporteMensualItemDTO

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"]
)

@router.get("/mensual", response_model=List[ReporteMensualItemDTO])
async def get_reporte_mensual(
    mes: int = Query(..., ge=1, le=12, description="Mes del reporte (1-12)"),
    anio: int = Query(..., ge=2000, description="Año del reporte"),
    personal_id: Optional[UUID] = Query(None, description="ID del personal para filtrar (opcional)")
):
    try:
        reporte = await ReporteService.generar_reporte_mensual(mes, anio, personal_id)
        return reporte
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
