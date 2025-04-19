"""
Servicio para la gestión de proyectos en TRIVO-AI.

Este servicio proporciona métodos para crear, consultar, actualizar y
eliminar proyectos, así como para gestionar los usuarios y recetas asociados.
"""
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.project import Project
from src.database.models.user import User
from src.database.models.recipe import Recipe
from src.database import db_session
from src.database.session import get_db_session

logger = logging.getLogger(__name__)

class ProjectService:
    """
    Servicio para la gestión de proyectos.
    
    Este servicio proporciona métodos para crear, consultar, actualizar
    y eliminar proyectos, así como para gestionar las relaciones con
    usuarios y recetas.
    """
    
    @staticmethod
    def create_project(
        name: str,
        description: str,
        creator_id: int,
        is_public: bool = False,
        status: str = "active",
        config: Dict[str, Any] = None,
        tags: List[str] = None
    ) -> Project:
        """
        Crea un nuevo proyecto.
        
        Args:
            name: Nombre del proyecto
            description: Descripción del proyecto
            creator_id: ID del usuario creador
            is_public: Si el proyecto es público o privado
            status: Estado inicial del proyecto (active, archived, completed)
            config: Configuración adicional del proyecto
            tags: Etiquetas para el proyecto
            
        Returns:
            El proyecto creado
            
        Raises:
            ValueError: Si faltan datos requeridos o son inválidos
            SQLAlchemyError: Si hay un error de base de datos
        """
        # Validación básica
        if not name:
            raise ValueError("El nombre del proyecto es obligatorio")
        
        if not creator_id:
            raise ValueError("Se requiere un usuario creador")
        
        # Crear proyecto
        project = Project(
            name=name,
            description=description,
            creator_id=creator_id,
            status=status,
            is_public=is_public,
            config=config or {},
            tags=tags or []
        )
        
        # Guardar en la base de datos
        try:
            with get_db_session() as db:
                # Verificar que el usuario creador existe
                creator = db.query(User).filter(User.id == creator_id).first()
                if not creator:
                    raise ValueError(f"No existe usuario con ID {creator_id}")
                
                # Guardar el proyecto
                db.add(project)
                db.flush()  # Para obtener el ID
                
                # Añadir al creador como miembro del proyecto
                project.users.append(creator)
                
                db.commit()
                db.refresh(project)
                
                logger.info(f"Proyecto creado: {project.id} - {project.name}")
                return project
        except SQLAlchemyError as e:
            logger.error(f"Error al crear proyecto: {str(e)}")
            raise
    
    @staticmethod
    def get_project_by_id(project_id: int) -> Optional[Project]:
        """
        Obtiene un proyecto por su ID.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            El proyecto o None si no existe
        """
        try:
            with get_db_session() as db:
                project = db.query(Project).filter(Project.id == project_id).first()
                return project
        except SQLAlchemyError as e:
            logger.error(f"Error al consultar proyecto {project_id}: {str(e)}")
            return None
    
    @staticmethod
    def update_project(
        project_id: int,
        data: Dict[str, Any]
    ) -> Optional[Project]:
        """
        Actualiza un proyecto existente.
        
        Args:
            project_id: ID del proyecto a actualizar
            data: Datos a actualizar
            
        Returns:
            El proyecto actualizado o None si no existe
        """
        try:
            with get_db_session() as db:
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project:
                    logger.warning(f"Proyecto no encontrado para actualizar: {project_id}")
                    return None
                
                # Actualizar campos
                if "name" in data and data["name"]:
                    project.name = data["name"]
                
                if "description" in data:
                    project.description = data["description"]
                
                if "status" in data:
                    project.status = data["status"]
                
                if "is_public" in data:
                    project.is_public = data["is_public"]
                
                if "config" in data:
                    project.config = data["config"]
                
                if "tags" in data:
                    project.tags = data["tags"]
                
                # Actualizar timestamp
                project.updated_at = datetime.utcnow()
                
                db.commit()
                db.refresh(project)
                
                logger.info(f"Proyecto actualizado: {project.id}")
                return project
        except SQLAlchemyError as e:
            logger.error(f"Error al actualizar proyecto {project_id}: {str(e)}")
            return None
    
    @staticmethod
    def delete_project(project_id: int) -> bool:
        """
        Elimina un proyecto.
        
        Args:
            project_id: ID del proyecto a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            with get_db_session() as db:
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project:
                    logger.warning(f"Proyecto no encontrado para eliminar: {project_id}")
                    return False
                
                db.delete(project)
                db.commit()
                
                logger.info(f"Proyecto eliminado: {project_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al eliminar proyecto {project_id}: {str(e)}")
            return False
    
    @staticmethod
    def list_projects(
        user_id: Optional[int] = None,
        status: Optional[str] = None,
        is_public: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Project]:
        """
        Lista proyectos con filtros opcionales.
        
        Args:
            user_id: Filtrar por usuario (creador o miembro)
            status: Filtrar por estado
            is_public: Filtrar por visibilidad
            limit: Número máximo de resultados
            offset: Desplazamiento para paginación
            
        Returns:
            Lista de proyectos
        """
        try:
            with get_db_session() as db:
                query = db.query(Project)
                
                # Aplicar filtros
                if user_id:
                    # Proyectos donde el usuario es creador o miembro
                    query = query.filter(
                        (Project.creator_id == user_id) | 
                        (Project.users.any(User.id == user_id))
                    )
                
                if status:
                    query = query.filter(Project.status == status)
                
                if is_public is not None:
                    query = query.filter(Project.is_public == is_public)
                
                # Ordenar por fecha de actividad y aplicar paginación
                query = query.order_by(desc(Project.last_activity))
                query = query.limit(limit).offset(offset)
                
                return query.all()
        except SQLAlchemyError as e:
            logger.error(f"Error al listar proyectos: {str(e)}")
            return []
    
    @staticmethod
    def add_user_to_project(project_id: int, user_id: int) -> bool:
        """
        Añade un usuario a un proyecto.
        
        Args:
            project_id: ID del proyecto
            user_id: ID del usuario a añadir
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        try:
            with get_db_session() as db:
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project:
                    logger.warning(f"Proyecto no encontrado: {project_id}")
                    return False
                
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.warning(f"Usuario no encontrado: {user_id}")
                    return False
                
                # Verificar si el usuario ya está en el proyecto
                if user in project.users:
                    logger.info(f"Usuario {user_id} ya es miembro del proyecto {project_id}")
                    return True
                
                # Añadir usuario
                project.users.append(user)
                project.last_activity = datetime.utcnow()
                db.commit()
                
                logger.info(f"Usuario {user_id} añadido al proyecto {project_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al añadir usuario {user_id} al proyecto {project_id}: {str(e)}")
            return False
    
    @staticmethod
    def remove_user_from_project(project_id: int, user_id: int) -> bool:
        """
        Elimina un usuario de un proyecto.
        
        Args:
            project_id: ID del proyecto
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            with get_db_session() as db:
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project:
                    logger.warning(f"Proyecto no encontrado: {project_id}")
                    return False
                
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.warning(f"Usuario no encontrado: {user_id}")
                    return False
                
                # No permitir eliminar al creador
                if project.creator_id == user_id:
                    logger.warning(f"No se puede eliminar al creador del proyecto: {user_id}")
                    return False
                
                # Verificar si el usuario está en el proyecto
                if user not in project.users:
                    logger.info(f"Usuario {user_id} no es miembro del proyecto {project_id}")
                    return True
                
                # Eliminar usuario
                project.users.remove(user)
                project.last_activity = datetime.utcnow()
                db.commit()
                
                logger.info(f"Usuario {user_id} eliminado del proyecto {project_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al eliminar usuario {user_id} del proyecto {project_id}: {str(e)}")
            return False
    
    @staticmethod
    def add_recipe_to_project(project_id: int, recipe_id: int) -> bool:
        """
        Añade una receta a un proyecto.
        
        Args:
            project_id: ID del proyecto
            recipe_id: ID de la receta a añadir
            
        Returns:
            True si se añadió correctamente, False en caso contrario
        """
        try:
            with get_db_session() as db:
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project:
                    logger.warning(f"Proyecto no encontrado: {project_id}")
                    return False
                
                recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
                if not recipe:
                    logger.warning(f"Receta no encontrada: {recipe_id}")
                    return False
                
                # Verificar si la receta ya está en el proyecto
                if recipe in project.recipes:
                    logger.info(f"Receta {recipe_id} ya está en el proyecto {project_id}")
                    return True
                
                # Añadir receta
                project.recipes.append(recipe)
                project.last_activity = datetime.utcnow()
                db.commit()
                
                logger.info(f"Receta {recipe_id} añadida al proyecto {project_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al añadir receta {recipe_id} al proyecto {project_id}: {str(e)}")
            return False
    
    @staticmethod
    def remove_recipe_from_project(project_id: int, recipe_id: int) -> bool:
        """
        Elimina una receta de un proyecto.
        
        Args:
            project_id: ID del proyecto
            recipe_id: ID de la receta a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            with get_db_session() as db:
                project = db.query(Project).filter(Project.id == project_id).first()
                if not project:
                    logger.warning(f"Proyecto no encontrado: {project_id}")
                    return False
                
                recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
                if not recipe:
                    logger.warning(f"Receta no encontrada: {recipe_id}")
                    return False
                
                # Verificar si la receta está en el proyecto
                if recipe not in project.recipes:
                    logger.info(f"Receta {recipe_id} no está en el proyecto {project_id}")
                    return True
                
                # Eliminar receta
                project.recipes.remove(recipe)
                project.last_activity = datetime.utcnow()
                db.commit()
                
                logger.info(f"Receta {recipe_id} eliminada del proyecto {project_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al eliminar receta {recipe_id} del proyecto {project_id}: {str(e)}")
            return False 