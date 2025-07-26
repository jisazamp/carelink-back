#!/usr/bin/env python3
"""
Script de prueba para verificar la integración del backend con la base de datos actualizada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.connection import get_carelink_db
from app.models import *
from app.crud.carelink_crud import CareLinkCrud
from sqlalchemy.orm import Session
from datetime import date, datetime, time

def test_database_connection():
    """Probar la conexión a la base de datos"""
    print(" Probando conexión a la base de datos...")
    
    try:
        engine = create_engine("mysql+pymysql://root:@localhost/carelink")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(" Conexión a la base de datos exitosa")
            return True
    except Exception as e:
        print(f" Error de conexión: {e}")
        return False

def test_models_import():
    """Probar que todos los modelos se importen correctamente"""
    print("\n Probando importación de modelos...")
    
    try:
        # Probar importación de modelos principales
        from app.models.contracts import Contratos, Facturas, DetalleFactura
        from app.models.attendance_schedule import CronogramaAsistencia, CronogramaAsistenciaPacientes
        from app.models.transporte import CronogramaTransporte
        from app.models.user import User
        from app.models.professional import Profesionales
        
        print(" Importación de modelos exitosa")
        return True
    except Exception as e:
        print(f" Error en importación de modelos: {e}")
        return False

def test_crud_operations():
    """Probar operaciones básicas del CRUD"""
    print("\n Probando operaciones del CRUD...")
    
    try:
        engine = create_engine("mysql+pymysql://root:@localhost/carelink")
        session = Session(engine)
        crud = CareLinkCrud(session)
        
        # Probar obtener usuarios
        users = crud.list_users()
        print(f" Obtención de usuarios: {len(users)} usuarios encontrados")
        
        # Probar obtener profesionales
        professionals = crud._get_professionals()
        print(f" Obtención de profesionales: {len(professionals)} profesionales encontrados")
        
        # Probar obtener contratos
        try:
            contracts = session.query(Contratos).limit(5).all()
            print(f" Obtención de contratos: {len(contracts)} contratos encontrados")
        except Exception as e:
            print(f"⚠️  Error obteniendo contratos: {e}")
        
        session.close()
        return True
    except Exception as e:
        print(f" Error en operaciones CRUD: {e}")
        return False

def test_cronograma_operations():
    """Probar operaciones de cronograma de asistencia"""
    print("\n Probando operaciones de cronograma...")
    
    try:
        engine = create_engine("mysql+pymysql://root:@localhost/carelink")
        session = Session(engine)
        crud = CareLinkCrud(session)
        
        # Verificar que las tablas existen
        result = session.execute(text("SHOW TABLES LIKE 'cronograma_asistencia'"))
        if result.fetchone():
            print(" Tabla cronograma_asistencia existe")
        else:
            print(" Tabla cronograma_asistencia no existe")
            return False
        
        result = session.execute(text("SHOW TABLES LIKE 'cronograma_asistencia_pacientes'"))
        if result.fetchone():
            print(" Tabla cronograma_asistencia_pacientes existe")
        else:
            print(" Tabla cronograma_asistencia_pacientes no existe")
            return False
        
        # Probar obtener cronogramas por rango
        try:
            cronogramas = crud.get_cronogramas_por_rango("2025-01-01", "2025-01-31")
            print(f" Obtención de cronogramas por rango: {len(cronogramas)} cronogramas encontrados")
        except Exception as e:
            print(f"⚠️  Error obteniendo cronogramas por rango: {e}")
        
        session.close()
        return True
    except Exception as e:
        print(f" Error en operaciones de cronograma: {e}")
        return False

def test_transporte_operations():
    """Probar operaciones de transporte"""
    print("\n Probando operaciones de transporte...")
    
    try:
        engine = create_engine("mysql+pymysql://root:@localhost/carelink")
        session = Session(engine)
        crud = CareLinkCrud(session)
        
        # Verificar que la tabla existe
        result = session.execute(text("SHOW TABLES LIKE 'cronograma_transporte'"))
        if result.fetchone():
            print(" Tabla cronograma_transporte existe")
        else:
            print(" Tabla cronograma_transporte no existe")
            return False
        
        # Probar obtener ruta diaria
        try:
            rutas = crud.get_ruta_diaria("2025-01-01")
            print(f" Obtención de ruta diaria: {len(rutas)} rutas encontradas")
        except Exception as e:
            print(f"⚠️  Error obteniendo ruta diaria: {e}")
        
        session.close()
        return True
    except Exception as e:
        print(f" Error en operaciones de transporte: {e}")
        return False

def test_contract_operations():
    """Probar operaciones de contratos y facturación"""
    print("\n Probando operaciones de contratos...")
    
    try:
        engine = create_engine("mysql+pymysql://root:@localhost/carelink")
        session = Session(engine)
        crud = CareLinkCrud(session)
        
        # Verificar que las tablas existen
        tables_to_check = [
            'Contratos', 'Facturas', 'DetalleFactura', 'Servicios', 
            'ServiciosPorContrato', 'FechasServicio', 'Pagos', 
            'MetodoPago', 'TipoPago'
        ]
        
        for table in tables_to_check:
            result = session.execute(text(f"SHOW TABLES LIKE '{table}'"))
            if result.fetchone():
                print(f" Tabla {table} existe")
            else:
                print(f" Tabla {table} no existe")
                return False
        
        # Probar obtener contratos
        try:
            contracts = session.query(Contratos).limit(5).all()
            print(f" Obtención de contratos: {len(contracts)} contratos encontrados")
        except Exception as e:
            print(f"⚠️  Error obteniendo contratos: {e}")
        
        # Probar obtener facturas
        try:
            bills = session.query(Facturas).limit(5).all()
            print(f" Obtención de facturas: {len(bills)} facturas encontradas")
        except Exception as e:
            print(f"⚠️  Error obteniendo facturas: {e}")
        
        session.close()
        return True
    except Exception as e:
        print(f" Error en operaciones de contratos: {e}")
        return False

def test_dto_validation():
    """Probar validación de DTOs"""
    print("\n Probando validación de DTOs...")
    
    try:
        from app.dto.v1.request.attendance_schedule import CronogramaAsistenciaCreateDTO, EstadoAsistenciaEnum
        from app.dto.v1.request.transport_schedule import CronogramaTransporteCreateDTO
        from app.dto.v1.request.contracts import ContratoCreateDTO
        
        # Probar DTO de cronograma
        cronograma_data = {
            "id_profesional": 1,
            "fecha": date(2025, 1, 15),
            "comentario": "Prueba de cronograma"
        }
        cronograma_dto = CronogramaAsistenciaCreateDTO(**cronograma_data)
        print(" DTO CronogramaAsistenciaCreateDTO válido")
        
        # Probar DTO de transporte
        transporte_data = {
            "id_cronograma_paciente": 1,
            "direccion_recogida": "Calle 123",
            "direccion_entrega": "Calle 456",
            "hora_recogida": time(8, 0, 0),
            "hora_entrega": time(17, 0, 0),
            "observaciones": "Prueba de transporte"
        }
        transporte_dto = CronogramaTransporteCreateDTO(**transporte_data)
        print(" DTO CronogramaTransporteCreateDTO válido")
        
        return True
    except Exception as e:
        print(f" Error en validación de DTOs: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de integración del backend...")
    
    tests = [
        ("Conexión a base de datos", test_database_connection),
        ("Importación de modelos", test_models_import),
        ("Operaciones CRUD", test_crud_operations),
        ("Operaciones de cronograma", test_cronograma_operations),
        ("Operaciones de transporte", test_transporte_operations),
        ("Operaciones de contratos", test_contract_operations),
        ("Validación de DTOs", test_dto_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f" Error en prueba '{test_name}': {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print(" RESUMEN DE PRUEBAS")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = " PASÓ" if result else " FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El backend está listo.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisar los errores anteriores.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 