"""
Endpoints de API para la gestión de proyectos en TRIVO-AI.

Este módulo proporciona endpoints REST para crear, consultar, 
actualizar y eliminar proyectos, así como para gestionar las
relaciones con usuarios y recetas.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field

from src.services.project_service import ProjectService
from src.utils.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectBase(BaseModel):
    """Modelo base para proyectos."""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del proyecto")
    description: Optional[str] = Field(None, description="Descripción del proyecto")
    is_public: bool = Field(False, description="Si el proyecto es público o privado")
    status: str = Field("active", description="Estado del proyecto (active, archived, completed)")
    tags: List[str] = Field(default_factory=list, description="Etiquetas del proyecto")
    config: Dict[str, Any] = Field(default_factory=dict, description="Configuración del proyecto")


class ProjectCreate(ProjectBase):
    """Modelo para crear proyectos."""
    pass


class ProjectUpdate(BaseModel):
    """Modelo para actualizar proyectos."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre del proyecto")
    description: Optional[str] = Field(None, description="Descripción del proyecto")
    is_public: Optional[bool] = Field(None, description="Si el proyecto es público o privado")
    status: Optional[str] = Field(None, description="Estado del proyecto (active, archived, completed)")
    tags: Optional[List[str]] = Field(None, description="Etiquetas del proyecto")
    config: Optional[Dict[str, Any]] = Field(None, description="Configuración del proyecto")


class ProjectResponse(ProjectBase):
    """Modelo de respuesta para proyectos."""
    id: int
    creator_id: int
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    user_count: int
    recipe_count: int

    class Config:
        orm_mode = True


@router.post("", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Crea un nuevo proyecto.
    
    El usuario actual será automáticamente el creador y miembro del proyecto.
    """
    try:
        new_project = ProjectService.create_project(
            name=project.name,
            description=project.description,
            creator_id=current_user["id"],
            is_public=project.is_public,
            status=project.status,
            config=project.config,
            tags=project.tags
        )
        return new_project.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el proyecto: {str(e)}")


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    status: Optional[str] = None,
    is_public: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista proyectos.
    
    Por defecto muestra los proyectos donde el usuario actual es creador o miembro.
    Los administradores pueden ver todos los proyectos si no filtran por usuario.
    """
    # Los administradores pueden ver todos los proyectos si no filtran
    user_id = None if current_user.get("role") == "admin" else current_user["id"]
    
    projects = ProjectService.list_projects(
        user_id=user_id,
        status=status,
        is_public=is_public,
        limit=limit,
        offset=offset
    )
    
    return [project.to_dict() for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int = Path(..., description="ID del proyecto"),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene un proyecto por su ID.
    
    Solo el creador, los miembros del proyecto y los administradores 
    pueden ver proyectos privados.
    """
    project = ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos para ver proyectos privados
    if not project.is_public:
        is_admin = current_user.get("role") == "admin"
        is_creator = project.creator_id == current_user["id"]
        
        # Verificar si el usuario es miembro del proyecto
        user_ids = [user.id for user in project.users]
        is_member = current_user["id"] in user_ids
        
        if not (is_admin or is_creator or is_member):
            raise HTTPException(
                status_code=403,
                detail="No tienes permisos para ver este proyecto"
            )
    
    return project.to_dict()


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_update: ProjectUpdate,
    project_id: int = Path(..., description="ID del proyecto"),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualiza un proyecto existente.
    
    Solo el creador del proyecto y los administradores pueden actualizarlo.
    """
    # Primero verificamos que exista el proyecto
    project = ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos
    is_admin = current_user.get("role") == "admin"
    is_creator = project.creator_id == current_user["id"]
    
    if not (is_admin or is_creator):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para actualizar este proyecto"
        )
    
    # Actualizar el proyecto
    updated_project = ProjectService.update_project(
        project_id=project_id,
        data=project_update.dict(exclude_unset=True)
    )
    
    if not updated_project:
        raise HTTPException(status_code=500, detail="Error al actualizar el proyecto")
    
    return updated_project.to_dict()


@router.delete("/{project_id}")
async def delete_project(
    project_id: int = Path(..., description="ID del proyecto"),
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un proyecto.
    
    Solo el creador del proyecto y los administradores pueden eliminarlo.
    """
    # Primero verificamos que exista el proyecto
    project = ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos
    is_admin = current_user.get("role") == "admin"
    is_creator = project.creator_id == current_user["id"]
    
    if not (is_admin or is_creator):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar este proyecto"
        )
    
    # Eliminar el proyecto
    success = ProjectService.delete_project(project_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar el proyecto")
    
    return {"message": "Proyecto eliminado correctamente"}


@router.post("/{project_id}/users/{user_id}")
async def add_user_to_project(
    project_id: int = Path(..., description="ID del proyecto"),
    user_id: int = Path(..., description="ID del usuario a añadir"),
    current_user: dict = Depends(get_current_user)
):
    """
    Añade un usuario al proyecto.
    
    Solo el creador del proyecto y los administradores pueden añadir usuarios.
    """
    # Primero verificamos que exista el proyecto
    project = ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos
    is_admin = current_user.get("role") == "admin"
    is_creator = project.creator_id == current_user["id"]
    
    if not (is_admin or is_creator):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para añadir usuarios a este proyecto"
        )
    
    # Añadir el usuario
    success = ProjectService.add_user_to_project(project_id, user_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Error al añadir el usuario al proyecto")
    
    return {"message": "Usuario añadido al proyecto correctamente"}


@router.delete("/{project_id}/users/{user_id}")
async def remove_user_from_project(
    project_id: int = Path(..., description="ID del proyecto"),
    user_id: int = Path(..., description="ID del usuario a eliminar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina un usuario del proyecto.
    
    Solo el creador del proyecto y los administradores pueden eliminar usuarios.
    No se puede eliminar al creador del proyecto.
    """
    # Primero verificamos que exista el proyecto
    project = ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos
    is_admin = current_user.get("role") == "admin"
    is_creator = project.creator_id == current_user["id"]
    
    if not (is_admin or is_creator):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar usuarios de este proyecto"
        )
    
    # No permitir eliminar al creador
    if project.creator_id == user_id:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar al creador del proyecto"
        )
    
    # Eliminar el usuario
    success = ProjectService.remove_user_from_project(project_id, user_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar el usuario del proyecto")
    
    return {"message": "Usuario eliminado del proyecto correctamente"}


@router.post("/{project_id}/recipes/{recipe_id}")
async def add_recipe_to_project(
    project_id: int = Path(..., description="ID del proyecto"),
    recipe_id: int = Path(..., description="ID de la receta a añadir"),
    current_user: dict = Depends(get_current_user)
):
    """
    Añade una receta al proyecto.
    
    Solo el creador y los miembros del proyecto pueden añadir recetas.
    """
    # Primero verificamos que exista el proyecto
    project = ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos
    is_admin = current_user.get("role") == "admin"
    is_creator = project.creator_id == current_user["id"]
    
    # Verificar si el usuario es miembro del proyecto
    user_ids = [user.id for user in project.users]
    is_member = current_user["id"] in user_ids
    
    if not (is_admin or is_creator or is_member):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para añadir recetas a este proyecto"
        )
    
    # Añadir la receta
    success = ProjectService.add_recipe_to_project(project_id, recipe_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Error al añadir la receta al proyecto")
    
    return {"message": "Receta añadida al proyecto correctamente"}


@router.delete("/{project_id}/recipes/{recipe_id}")
async def remove_recipe_from_project(
    project_id: int = Path(..., description="ID del proyecto"),
    recipe_id: int = Path(..., description="ID de la receta a eliminar"),
    current_user: dict = Depends(get_current_user)
):
    """
    Elimina una receta del proyecto.
    
    Solo el creador y los miembros del proyecto pueden eliminar recetas.
    """
    # Primero verificamos que exista el proyecto
    project = ProjectService.get_project_by_id(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    
    # Verificar permisos
    is_admin = current_user.get("role") == "admin"
    is_creator = project.creator_id == current_user["id"]
    
    # Verificar si el usuario es miembro del proyecto
    user_ids = [user.id for user in project.users]
    is_member = current_user["id"] in user_ids
    
    if not (is_admin or is_creator or is_member):
        raise HTTPException(
            status_code=403,
            detail="No tienes permisos para eliminar recetas de este proyecto"
        )
    
    # Eliminar la receta
    success = ProjectService.remove_recipe_from_project(project_id, recipe_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Error al eliminar la receta del proyecto")
    
    return {"message": "Receta eliminada del proyecto correctamente"} 