#!/usr/bin/env python3
"""
Script de debug para verificar el estado de las tablas de cronograma
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.connection import get_carelink_db
from sqlalchemy.orm import Session

def check_tables():
    """Verifica que las tablas de cronograma existan y tengan la estructura correcta"""
    
    # Obtener conexión a la base de datos
    engine = create_engine("mysql+pymysql://root:@localhost/carelink")
    
    with engine.connect() as connection:
        print("🔍 Verificando estructura de tablas...")
        
        # Verificar tabla cronograma_asistencia
        try:
            result = connection.execute(text("""
                DESCRIBE cronograma_asistencia
            """))
            print("\n✅ Tabla cronograma_asistencia existe:")
            for row in result:
                print(f"  - {row[0]}: {row[1]}")
        except Exception as e:
            print(f"❌ Error con tabla cronograma_asistencia: {e}")
        
        # Verificar tabla cronograma_asistencia_pacientes
        try:
            result = connection.execute(text("""
                DESCRIBE cronograma_asistencia_pacientes
            """))
            print("\n✅ Tabla cronograma_asistencia_pacientes existe:")
            for row in result:
                print(f"  - {row[0]}: {row[1]}")
        except Exception as e:
            print(f"❌ Error con tabla cronograma_asistencia_pacientes: {e}")
        
        # Verificar tabla cronograma_transporte
        try:
            result = connection.execute(text("""
                DESCRIBE cronograma_transporte
            """))
            print("\n✅ Tabla cronograma_transporte existe:")
            for row in result:
                print(f"  - {row[0]}: {row[1]}")
        except Exception as e:
            print(f"❌ Error con tabla cronograma_transporte: {e}")
        
        # Verificar datos existentes
        print("\n📊 Datos existentes:")
        
        try:
            result = connection.execute(text("SELECT COUNT(*) FROM cronograma_asistencia"))
            count = result.scalar()
            print(f"  - cronograma_asistencia: {count} registros")
        except Exception as e:
            print(f"  - cronograma_asistencia: Error - {e}")
        
        try:
            result = connection.execute(text("SELECT COUNT(*) FROM cronograma_asistencia_pacientes"))
            count = result.scalar()
            print(f"  - cronograma_asistencia_pacientes: {count} registros")
        except Exception as e:
            print(f"  - cronograma_asistencia_pacientes: Error - {e}")
        
        try:
            result = connection.execute(text("SELECT COUNT(*) FROM cronograma_transporte"))
            count = result.scalar()
            print(f"  - cronograma_transporte: {count} registros")
        except Exception as e:
            print(f"  - cronograma_transporte: Error - {e}")
        
        # Verificar contratos existentes
        try:
            result = connection.execute(text("SELECT id_contrato, id_usuario, tipo_contrato FROM Contratos ORDER BY id_contrato DESC LIMIT 5"))
            print(f"\n📋 Últimos 5 contratos:")
            for row in result:
                print(f"  - Contrato {row[0]}: Usuario {row[1]}, Tipo: {row[2]}")
        except Exception as e:
            print(f"  - Error consultando contratos: {e}")

def test_contrato_creation():
    """Simula la creación de un contrato para verificar el proceso"""
    
    print("\n🧪 Simulando creación de contrato...")
    
    # Datos de prueba
    test_data = {
        "id_usuario": 1,
        "tipo_contrato": "Nuevo",
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-02-01",
        "facturar_contrato": True,
        "servicios": [
            {
                "id_servicio": 1,
                "fecha": "2025-01-01",
                "descripcion": "Tiquetera 1",
                "precio_por_dia": 50000,
                "fechas_servicio": [
                    {"fecha": "2025-01-01"},
                    {"fecha": "2025-01-02"},
                    {"fecha": "2025-01-03"}
                ]
            },
            {
                "id_servicio": 2,
                "fecha": "2025-01-01",
                "descripcion": "Transporte 1",
                "precio_por_dia": 30000,
                "fechas_servicio": [
                    {"fecha": "2025-01-01"},
                    {"fecha": "2025-01-02"}
                ]
            }
        ]
    }
    
    print(f"📝 Datos de prueba:")
    print(f"  - Usuario: {test_data['id_usuario']}")
    print(f"  - Tipo: {test_data['tipo_contrato']}")
    print(f"  - Fechas: {test_data['fecha_inicio']} a {test_data['fecha_fin']}")
    print(f"  - Servicios: {len(test_data['servicios'])}")
    
    for servicio in test_data['servicios']:
        print(f"    * Servicio {servicio['id_servicio']}: {len(servicio['fechas_servicio'])} fechas")

if __name__ == "__main__":
    print("🚀 Iniciando debug de contratos y cronogramas...")
    check_tables()
    test_contrato_creation()
    print("\n✅ Debug completado") 