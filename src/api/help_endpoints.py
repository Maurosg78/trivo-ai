from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from src.database.models.help_log import HelpType
from src.services.help_service import HelpService
from src.utils.auth import get_current_user

router = APIRouter(prefix="/help", tags=["help"])


class HelpLogResponse(BaseModel):
    """Modelo de respuesta para registros de ayuda."""
    id: int
    user_id: str
    help_type: str
    query: str
    response: str
    recipe_id: Optional[str] = None
    context_data: dict = {}
    created_at: datetime


class HelpStatisticsResponse(BaseModel):
    """Modelo de respuesta para estadísticas de ayuda."""
    total_help_interactions: int
    help_type_distribution: dict
    recent_interactions: List[HelpLogResponse]


@router.get("/history", response_model=List[HelpLogResponse])
async def get_help_history(
    user_id: Optional[str] = None,
    recipe_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene el historial de interacciones de ayuda.
    
    Se puede filtrar por usuario o receta.
    """
    if user_id:
        # Asegurar que solo los administradores puedan ver el historial de otros usuarios
        if current_user.get("role") != "admin" and user_id != current_user.get("id"):
            raise HTTPException(
                status_code=403,
                detail="No tienes permiso para ver el historial de este usuario"
            )
        return HelpService.get_user_help_history(user_id, limit=limit, offset=offset)
    
    if recipe_id:
        # Verificar si el usuario tiene acceso a esta receta
        # Esto dependerá de la lógica de tu aplicación
        return HelpService.get_recipe_help_history(recipe_id, limit=limit, offset=offset)
    
    # Si no se especifica, devolver el historial del usuario actual
    return HelpService.get_user_help_history(current_user.get("id"), limit=limit, offset=offset)


@router.get("/search", response_model=List[HelpLogResponse])
async def search_help_logs(
    query_text: Optional[str] = None,
    help_type: Optional[str] = None,
    user_id: Optional[str] = None,
    recipe_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Busca registros de ayuda con varios criterios.
    
    Solo los administradores pueden buscar en todos los registros.
    """
    # Verificar permisos
    if current_user.get("role") != "admin":
        # Los usuarios normales solo pueden buscar en sus propios registros
        user_id = current_user.get("id")
    
    # Convertir el string de help_type a enum si se proporciona
    help_type_enum = None
    if help_type:
        try:
            help_type_enum = HelpType[help_type]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de ayuda inválido: {help_type}. Opciones válidas: {[t.name for t in HelpType]}"
            )
    
    return HelpService.search_help_logs(
        query_text=query_text,
        help_type=help_type_enum,
        user_id=user_id,
        recipe_id=recipe_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )


@router.get("/statistics", response_model=HelpStatisticsResponse)
async def get_help_statistics(
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene estadísticas generales de las interacciones de ayuda.
    
    Solo disponible para administradores.
    """
    # Verificar que sea administrador
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden acceder a las estadísticas"
        )
    
    return HelpService.get_help_statistics()


@router.delete("/{log_id}", response_model=bool)
async def delete_help_log(
    log_id: int,
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un registro de ayuda específico.
    
    Solo disponible para administradores.
    """
    # Verificar que sea administrador
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Solo los administradores pueden eliminar registros"
        )
    
    result = HelpService.delete_help_log(log_id)
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Registro de ayuda con ID {log_id} no encontrado"
        )
    
    return True 