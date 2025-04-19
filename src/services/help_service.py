"""
Servicio para gestionar y registrar las interacciones de ayuda en TRIVO-AI.

Este servicio proporciona métodos para registrar, consultar y analizar
las interacciones de ayuda generadas por el sistema.
"""
import logging
from typing import Dict, List, Optional, Union, Any, Tuple, cast
from datetime import datetime
import json

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.help_log import HelpLog, HelpType
from src.database import db_session
from src.database.session import get_db_session

logger = logging.getLogger(__name__)

class HelpService:
    """
    Servicio para gestionar el registro y consulta de interacciones de ayuda.
    
    Este servicio proporciona métodos para registrar nuevas interacciones de ayuda,
    consultar el historial de ayuda por usuario o receta, y obtener estadísticas
    sobre las interacciones registradas.
    """
    
    @staticmethod
    def register_help(
        user_id: str,
        help_type: Union[HelpType, str],
        query: str,
        response: str,
        context_data: Optional[Dict[str, Any]] = None,
        recipe_id: Optional[str] = None
    ) -> HelpLog:
        """
        Registra una nueva interacción de ayuda en la base de datos.
        
        Args:
            user_id: ID del usuario que recibió la ayuda
            help_type: Tipo de ayuda proporcionada
            query: Consulta o pregunta del usuario
            response: Respuesta proporcionada por el sistema
            context_data: Datos adicionales de contexto (opcional)
            recipe_id: ID de la receta relacionada (opcional)
            
        Returns:
            El registro de ayuda creado
            
        Raises:
            ValueError: Si el tipo de ayuda no es válido
        """
        # Validar y convertir el tipo de ayuda
        if isinstance(help_type, str):
            try:
                help_type = HelpType[help_type]
            except KeyError:
                # Verificamos si el valor está en los valores de la enumeración
                help_type_values = [ht.value for ht in HelpType]
                if help_type in help_type_values:
                    help_type = HelpType(help_type)
                else:
                    logger.warning(f"Tipo de ayuda no válido: {help_type}")
                    help_type = HelpType.OTHER
        
        # Convertir los datos de contexto a cadena JSON si existen
        context_json = None
        if context_data:
            try:
                context_json = json.dumps(context_data, default=str)
            except Exception as e:
                logger.error(f"Error al serializar datos de contexto: {str(e)}")
                # Intentar una serialización más simple
                try:
                    context_json = json.dumps({"error": "Error de serialización", "data_str": str(context_data)})
                except:
                    context_json = json.dumps({"error": "Error completo de serialización"})
        
        # Crear el registro
        help_log = HelpLog(
            user_id=user_id,
            help_type=help_type,
            query=query,
            response=response,
            context_data=context_json,
            recipe_id=recipe_id,
            timestamp=datetime.utcnow()
        )
        
        # Guardar en la base de datos
        try:
            with get_db_session() as db:
                db.add(help_log)
                db.commit()
                db.refresh(help_log)
                logger.info(f"Registrada interacción de ayuda ID: {help_log.id} para usuario: {user_id}")
                return help_log
        except SQLAlchemyError as e:
            logger.error(f"Error al registrar interacción de ayuda: {str(e)}")
            # Devolvemos un objeto dummy con ID -1 para no interrumpir el flujo
            dummy_log = HelpLog(
                id=-1,
                user_id=user_id,
                help_type=help_type,
                query=query,
                response="ERROR: No se pudo registrar",
                timestamp=datetime.utcnow()
            )
            return dummy_log
    
    @staticmethod
    def get_user_help_history(
        user_id: str,
        help_type: Optional[Union[HelpType, str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[HelpLog]:
        """
        Obtiene el historial de interacciones de ayuda para un usuario.
        
        Args:
            user_id: ID del usuario
            help_type: Filtrar por tipo de ayuda (opcional)
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de registros de ayuda ordenados por fecha (más recientes primero)
        """
        try:
            with get_db_session() as db:
                query = db.query(HelpLog).filter(HelpLog.user_id == user_id)
                
                # Aplicar filtro por tipo si se especifica
                if help_type:
                    if isinstance(help_type, str):
                        try:
                            help_type = HelpType[help_type]
                        except KeyError:
                            # Verificamos si el valor está en los valores de la enumeración
                            help_type_values = [ht.value for ht in HelpType]
                            if help_type in help_type_values:
                                help_type = HelpType(help_type)
                            else:
                                logger.warning(f"Tipo de ayuda no válido para filtrado: {help_type}")
                                return []
                    
                    query = query.filter(HelpLog.help_type == help_type)
                
                # Ordenar por fecha descendente y aplicar paginación
                result = query.order_by(HelpLog.timestamp.desc()).limit(limit).offset(offset).all()
                return result
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener historial de ayuda del usuario {user_id}: {str(e)}")
            return []
    
    @staticmethod
    def get_recipe_help_history(
        recipe_id: str,
        help_type: Optional[Union[HelpType, str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[HelpLog]:
        """
        Obtiene el historial de interacciones de ayuda para una receta.
        
        Args:
            recipe_id: ID de la receta
            help_type: Filtrar por tipo de ayuda (opcional)
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Lista de registros de ayuda ordenados por fecha (más recientes primero)
        """
        try:
            with get_db_session() as db:
                query = db.query(HelpLog).filter(HelpLog.recipe_id == recipe_id)
                
                # Aplicar filtro por tipo si se especifica
                if help_type:
                    if isinstance(help_type, str):
                        try:
                            help_type = HelpType[help_type]
                        except KeyError:
                            # Verificamos si el valor está en los valores de la enumeración
                            help_type_values = [ht.value for ht in HelpType]
                            if help_type in help_type_values:
                                help_type = HelpType(help_type)
                            else:
                                logger.warning(f"Tipo de ayuda no válido para filtrado: {help_type}")
                                return []
                    
                    query = query.filter(HelpLog.help_type == help_type)
                
                # Ordenar por fecha descendente y aplicar paginación
                result = query.order_by(HelpLog.timestamp.desc()).limit(limit).offset(offset).all()
                return result
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener historial de ayuda de la receta {recipe_id}: {str(e)}")
            return []
    
    @staticmethod
    def get_help_statistics() -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre las interacciones de ayuda registradas.
        
        Returns:
            Diccionario con estadísticas generales y por tipo de ayuda
        """
        stats = {
            "total_interactions": 0,
            "interactions_by_type": {},
            "unique_users_assisted": 0,
            "unique_recipes_assisted": 0
        }
        
        try:
            with get_db_session() as db:
                # Total de interacciones
                stats["total_interactions"] = db.query(HelpLog).count()
                
                # Interacciones por tipo
                for help_type in HelpType:
                    count = db.query(HelpLog).filter(HelpLog.help_type == help_type).count()
                    stats["interactions_by_type"][help_type.name] = count
                
                # Usuarios únicos asistidos
                stats["unique_users_assisted"] = db.query(HelpLog.user_id).distinct().count()
                
                # Recetas únicas asistidas (excluyendo nulls)
                stats["unique_recipes_assisted"] = db.query(HelpLog.recipe_id).filter(
                    HelpLog.recipe_id.is_not(None)
                ).distinct().count()
                
                return stats
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener estadísticas de ayuda: {str(e)}")
            return stats
    
    @staticmethod
    def search_help_logs(
        query_text: Optional[str] = None,
        help_type: Optional[Union[HelpType, str]] = None,
        user_id: Optional[str] = None,
        recipe_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[HelpLog], int]:
        """
        Busca registros de ayuda con filtros combinados.
        
        Args:
            query_text: Texto a buscar en la consulta o respuesta
            help_type: Filtrar por tipo de ayuda
            user_id: Filtrar por ID de usuario
            recipe_id: Filtrar por ID de receta
            date_from: Fecha inicial para filtrar
            date_to: Fecha final para filtrar
            limit: Número máximo de registros a devolver
            offset: Número de registros a omitir
            
        Returns:
            Tupla con la lista de registros y el conteo total
        """
        try:
            with get_db_session() as db:
                query = db.query(HelpLog)
                
                # Aplicar filtros
                if query_text:
                    query = query.filter(
                        (HelpLog.query.ilike(f"%{query_text}%")) | 
                        (HelpLog.response.ilike(f"%{query_text}%"))
                    )
                
                if help_type:
                    if isinstance(help_type, str):
                        try:
                            help_type = HelpType[help_type]
                        except KeyError:
                            help_type_values = [ht.value for ht in HelpType]
                            if help_type in help_type_values:
                                help_type = HelpType(help_type)
                            else:
                                logger.warning(f"Tipo de ayuda no válido para búsqueda: {help_type}")
                                return [], 0
                    
                    query = query.filter(HelpLog.help_type == help_type)
                
                if user_id:
                    query = query.filter(HelpLog.user_id == user_id)
                
                if recipe_id:
                    query = query.filter(HelpLog.recipe_id == recipe_id)
                
                if date_from:
                    query = query.filter(HelpLog.timestamp >= date_from)
                
                if date_to:
                    query = query.filter(HelpLog.timestamp <= date_to)
                
                # Obtener conteo total
                total_count = query.count()
                
                # Aplicar ordenamiento y paginación
                results = query.order_by(HelpLog.timestamp.desc()).limit(limit).offset(offset).all()
                
                return results, total_count
        except SQLAlchemyError as e:
            logger.error(f"Error en búsqueda de registros de ayuda: {str(e)}")
            return [], 0
    
    @staticmethod
    def delete_help_log(log_id: int) -> bool:
        """
        Elimina un registro de ayuda de la base de datos.
        
        Args:
            log_id: ID del registro a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        try:
            with get_db_session() as db:
                log = db.query(HelpLog).filter(HelpLog.id == log_id).first()
                if not log:
                    logger.warning(f"Registro de ayuda no encontrado: {log_id}")
                    return False
                
                db.delete(log)
                db.commit()
                logger.info(f"Eliminado registro de ayuda ID: {log_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al eliminar registro de ayuda {log_id}: {str(e)}")
            return False

    @staticmethod
    def update_feedback(
        help_log_id: str,
        feedback: str,
        usefulness_rating: Optional[int] = None,
        db: Session = None
    ) -> Optional[HelpLog]:
        """
        Actualiza el feedback de un registro de ayuda existente.
        
        Args:
            help_log_id: ID del registro de ayuda
            feedback: Comentario de retroalimentación del usuario
            usefulness_rating: Calificación de utilidad (1-5)
            db: Sesión de base de datos (opcional)
            
        Returns:
            Registro actualizado o None si no se encuentra
        """
        session_provided = db is not None
        db = db or db_session()
        
        try:
            help_log = db.query(HelpLog).filter(HelpLog.id == help_log_id).first()
            if not help_log:
                logger.warning(f"No se encontró registro de ayuda con ID {help_log_id}")
                return None
            
            help_log.feedback = feedback
            if usefulness_rating is not None:
                help_log.usefulness_rating = max(1, min(5, usefulness_rating))  # Asegurar rango 1-5
            
            if not session_provided:
                db.commit()
            
            logger.info(f"Actualizado feedback para registro de ayuda {help_log_id}")
            return help_log
        except Exception as e:
            if not session_provided:
                db.rollback()
            logger.error(f"Error al actualizar feedback: {str(e)}")
            raise
        finally:
            if not session_provided:
                db.close()
    
    @staticmethod
    def get_help_stats(db: Session = None) -> Dict[str, Any]:
        """
        Obtiene estadísticas sobre las ayudas proporcionadas.
        
        Args:
            db: Sesión de base de datos (opcional)
            
        Returns:
            Diccionario con estadísticas
        """
        session_provided = db is not None
        db = db or db_session()
        
        try:
            # Total de registros
            total_count = db.query(func.count(HelpLog.id)).scalar() or 0
            
            # Conteo por tipo de ayuda
            type_counts = {}
            for help_type in HelpType:
                count = db.query(func.count(HelpLog.id)).filter(
                    HelpLog.help_type == help_type
                ).scalar() or 0
                type_counts[help_type.value] = count
            
            # Promedio de calificación de utilidad
            avg_rating = db.query(func.avg(HelpLog.usefulness_rating)).filter(
                HelpLog.usefulness_rating.isnot(None)
            ).scalar() or 0
            
            return {
                "total_count": total_count,
                "by_type": type_counts,
                "average_rating": float(avg_rating),
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de ayuda: {str(e)}")
            raise
        finally:
            if not session_provided:
                db.close()

    @staticmethod
    def export_help_data(start_date=None, end_date=None, format="json") -> str:
        """
        Exporta los datos de ayuda en un formato específico.
        
        Args:
            start_date: Fecha inicial para filtrar (opcional)
            end_date: Fecha final para filtrar (opcional)
            format: Formato de exportación ('json' o 'csv')
            
        Returns:
            String con los datos exportados
        """
        db = db_session()
        
        try:
            query = db.query(HelpLog)
            
            # Aplicar filtros de fecha si se proporcionan
            if start_date:
                query = query.filter(HelpLog.created_at >= start_date)
            if end_date:
                query = query.filter(HelpLog.created_at <= end_date)
            
            # Ejecutar consulta
            results = query.all()
            
            # Convertir a formato solicitado
            if format.lower() == "json":
                data = [log.to_dict() for log in results]
                return json.dumps(data, indent=2)
            elif format.lower() == "csv":
                # Implementación simple CSV
                headers = ["id", "user_id", "help_type", "created_at", "usefulness_rating"]
                rows = [",".join(headers)]
                
                for log in results:
                    row = [
                        log.id,
                        log.user_id,
                        log.help_type.value if log.help_type else "N/A",
                        log.created_at.isoformat() if log.created_at else "N/A",
                        str(log.usefulness_rating) if log.usefulness_rating else "N/A"
                    ]
                    rows.append(",".join(row))
                
                return "\n".join(rows)
            else:
                raise ValueError(f"Formato no soportado: {format}")
        except Exception as e:
            logger.error(f"Error al exportar datos de ayuda: {str(e)}")
            raise
        finally:
            db.close() 