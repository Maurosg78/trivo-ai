import os
import sys
import subprocess
from pathlib import Path

def run_command(command: str) -> None:
    """Ejecuta un comando y maneja errores."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {command}")
        print(f"Error: {e}")
        sys.exit(1)

def main():
    # Verificar que estamos en el directorio correcto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Instalar dependencias
    print("Instalando dependencias...")
    run_command("pip install -r requirements.txt")
    
    # Crear base de datos si no existe
    print("Creando base de datos...")
    run_command("createdb pizzaai || true")
    
    # Ejecutar migraciones
    print("Ejecutando migraciones...")
    run_command("alembic upgrade head")
    
    # Crear usuario admin inicial
    print("Creando usuario admin inicial...")
    from src.core.models import User, UserRole
    from src.core.config import get_settings
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    settings = get_settings()
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@pizzaai.com").first()
        if not admin:
            admin = User(
                email="admin@pizzaai.com",
                username="admin",
                hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: admin
                full_name="Administrador",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("Usuario admin creado exitosamente")
        else:
            print("Usuario admin ya existe")
    except Exception as e:
        print(f"Error creando usuario admin: {e}")
        db.rollback()
    finally:
        db.close()
    
    print("Inicialización completada exitosamente")

if __name__ == "__main__":
    main() 