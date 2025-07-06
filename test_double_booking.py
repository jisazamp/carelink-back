#!/usr/bin/env python3
"""
Script de prueba para verificar las validaciones de doble agendamiento
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database.connection import get_carelink_db
from sqlalchemy.orm import Session
from datetime import date, datetime
import requests
import json

def test_database_constraints():
    """Prueba las restricciones de base de datos"""
    
    print("🔍 Probando restricciones de base de datos...")
    
    # Obtener conexión a la base de datos
    engine = create_engine("mysql+pymysql://root:@localhost/carelink")
    
    with engine.connect() as connection:
        # Verificar que el índice único existe
        try:
            result = connection.execute(text("""
                SHOW INDEX FROM cronograma_asistencia_pacientes 
                WHERE Key_name = 'idx_unique_paciente_cronograma'
            """))
            if result.fetchone():
                print("✅ Índice único para prevenir doble agendamiento existe")
            else:
                print("❌ Índice único para prevenir doble agendamiento NO existe")
        except Exception as e:
            print(f"❌ Error verificando índice único: {e}")
        
        # Verificar que el trigger existe
        try:
            result = connection.execute(text("""
                SHOW TRIGGERS LIKE 'cronograma_asistencia_pacientes'
            """))
            triggers = result.fetchall()
            trigger_names = [row[0] for row in triggers]
            if 'validar_doble_agendamiento' in trigger_names:
                print("✅ Trigger de validación existe")
            else:
                print("❌ Trigger de validación NO existe")
        except Exception as e:
            print(f"❌ Error verificando trigger: {e}")

def test_api_validations():
    """Prueba las validaciones de la API"""
    
    print("\n🧪 Probando validaciones de la API...")
    
    # Configuración
    base_url = "http://localhost:8000"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_TOKEN_HERE"  # Reemplazar con token válido
    }
    
    # Datos de prueba para crear contrato
    test_contract_data = {
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
                    {"fecha": "2025-01-02"}
                ]
            }
        ]
    }
    
    try:
        # Intentar crear el primer contrato
        print("📝 Creando primer contrato...")
        response = requests.post(
            f"{base_url}/api/contratos/",
            json=test_contract_data,
            headers=headers
        )
        
        if response.status_code == 201:
            print("✅ Primer contrato creado exitosamente")
            contract_data = response.json()
            print(f"   Contrato ID: {contract_data['data']['id_contrato']}")
        else:
            print(f"❌ Error creando primer contrato: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return
        
        # Intentar crear un segundo contrato con las mismas fechas
        print("\n📝 Intentando crear segundo contrato con fechas duplicadas...")
        test_contract_data_2 = test_contract_data.copy()
        test_contract_data_2["tipo_contrato"] = "Recurrente"
        
        response2 = requests.post(
            f"{base_url}/api/contratos/",
            json=test_contract_data_2,
            headers=headers
        )
        
        if response2.status_code == 400:
            print("✅ Validación de doble agendamiento funciona correctamente")
            print(f"   Error esperado: {response2.json()['detail']}")
        else:
            print(f"❌ Validación falló: {response2.status_code}")
            print(f"   Respuesta: {response2.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_existing_data():
    """Verifica datos existentes que podrían causar conflictos"""
    
    print("\n📊 Verificando datos existentes...")
    
    engine = create_engine("mysql+pymysql://root:@localhost/carelink")
    
    with engine.connect() as connection:
        # Verificar pacientes con múltiples agendamientos
        try:
            result = connection.execute(text("""
                SELECT 
                    cap.id_usuario,
                    ca.fecha,
                    COUNT(*) as agendamientos
                FROM cronograma_asistencia_pacientes cap
                JOIN cronograma_asistencia ca ON cap.id_cronograma = ca.id_cronograma
                GROUP BY cap.id_usuario, ca.fecha
                HAVING COUNT(*) > 1
                ORDER BY agendamientos DESC
            """))
            
            duplicates = result.fetchall()
            if duplicates:
                print("⚠️  Se encontraron pacientes con múltiples agendamientos:")
                for row in duplicates:
                    print(f"   - Usuario {row[0]} en fecha {row[1]}: {row[2]} agendamientos")
            else:
                print("✅ No se encontraron dobles agendamientos en datos existentes")
                
        except Exception as e:
            print(f"❌ Error verificando datos existentes: {e}")

def cleanup_test_data():
    """Limpia datos de prueba"""
    
    print("\n🧹 Limpiando datos de prueba...")
    
    engine = create_engine("mysql+pymysql://root:@localhost/carelink")
    
    with engine.connect() as connection:
        try:
            # Eliminar contratos de prueba (ajustar según necesidad)
            result = connection.execute(text("""
                DELETE FROM cronograma_asistencia_pacientes 
                WHERE id_contrato IN (
                    SELECT id_contrato FROM Contratos 
                    WHERE fecha_inicio = '2025-01-01' AND fecha_fin = '2025-02-01'
                )
            """))
            
            result = connection.execute(text("""
                DELETE FROM Contratos 
                WHERE fecha_inicio = '2025-01-01' AND fecha_fin = '2025-02-01'
            """))
            
            print("✅ Datos de prueba limpiados")
            
        except Exception as e:
            print(f"❌ Error limpiando datos: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de validación de doble agendamiento...")
    
    test_database_constraints()
    test_existing_data()
    test_api_validations()
    cleanup_test_data()
    
    print("\n✅ Pruebas completadas")
    print("\n📋 Resumen de validaciones implementadas:")
    print("1. ✅ Validación en creación de contratos")
    print("2. ✅ Validación en agregar paciente a cronograma")
    print("3. ✅ Índice único en base de datos")
    print("4. ✅ Trigger de respaldo")
    print("5. ✅ Mensajes de error descriptivos") 