#!/usr/bin/env python3
"""
Script de prueba para verificar la implementación completa de facturación
"""

import requests
import json
from datetime import date, datetime

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login"

def test_facturacion_completa():
    """Prueba completa del sistema de facturación"""
    
    print(" Iniciando pruebas de facturación completa...")
    
    # 1. Login para obtener token
    print("\n1. Obteniendo token de autenticación...")
    login_data = {
        "email": "davidrestrepovera@gmail.com",
        "password": "Banano1243"
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        if login_response.status_code != 200:
            print(f" Error en login: {login_response.status_code}")
            print(f"Respuesta: {login_response.text}")
            return
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(" Login exitoso")
        
    except Exception as e:
        print(f" Error en login: {e}")
        return

    # 2. Probar cálculo de total de factura
    print("\n2. Probando cálculo de total de factura...")
    
    calculo_data = {
        "subtotal": 100000.0,
        "impuestos": 5000.0,
        "descuentos": 2000.0
    }
    
    try:
        calculo_response = requests.post(
            f"{BASE_URL}/api/calcular/total_factura",
            json=calculo_data,
            headers=headers
        )
        
        print(f"Status Code: {calculo_response.status_code}")
        print(f"Respuesta: {calculo_response.text}")
        
        if calculo_response.status_code == 200:
            total_calculado = calculo_response.json()["data"]
            print(f" Total calculado: {total_calculado}")
            print(f" Verificación: 100000 + 5000 - 2000 = {100000 + 5000 - 2000}")
        else:
            print(" Error al calcular total de factura")
            
    except Exception as e:
        print(f" Error en cálculo: {e}")

    # 3. Probar creación de contrato con validación de doble agendamiento
    print("\n3. Probando creación de contrato...")
    
    contrato_data = {
        "id_usuario": 2,
        "tipo_contrato": "Nuevo",
        "fecha_inicio": "2025-07-21",
        "fecha_fin": "2025-08-21",
        "facturar_contrato": True,
        "servicios": [
            {
                "id_servicio": 1,
                "fecha": "2025-07-21",
                "descripcion": "Servicio de tiquetera",
                "precio_por_dia": 0,
                "fechas_servicio": [
                    {"fecha": "2025-07-21"},
                    {"fecha": "2025-07-22"},
                    {"fecha": "2025-07-23"},
                    {"fecha": "2025-07-24"}
                ]
            },
            {
                "id_servicio": 2,
                "fecha": "2025-07-21",
                "descripcion": "Servicio de transporte",
                "precio_por_dia": 0,
                "fechas_servicio": [
                    {"fecha": "2025-07-21"},
                    {"fecha": "2025-07-22"},
                    {"fecha": "2025-07-23"},
                    {"fecha": "2025-07-24"}
                ]
            }
        ]
    }
    
    try:
        contrato_response = requests.post(
            f"{BASE_URL}/api/contratos/",
            json=contrato_data,
            headers=headers
        )
        
        print(f"Status Code: {contrato_response.status_code}")
        print(f"Respuesta: {contrato_response.text}")
        
        if contrato_response.status_code == 201:
            contrato_id = contrato_response.json()["data"]["id_contrato"]
            print(f" Contrato creado con ID: {contrato_id}")
            
            # 4. Probar creación de factura con datos completos
            print("\n4. Probando creación de factura con datos completos...")
            
            factura_data = {
                "impuestos": 5000.0,
                "descuentos": 2000.0,
                "observaciones": "Factura generada automáticamente desde el contrato"
            }
            
            factura_response = requests.post(
                f"{BASE_URL}/api/facturas/{contrato_id}",
                json=factura_data,
                headers=headers
            )
            
            print(f"Status Code: {factura_response.status_code}")
            print(f"Respuesta: {factura_response.text}")
            
            if factura_response.status_code == 201:
                factura = factura_response.json()["data"]
                print(f" Factura creada con ID: {factura['id_factura']}")
                print(f" Fecha vencimiento: {factura['fecha_vencimiento']}")
                print(f" Subtotal: {factura['subtotal']}")
                print(f" Impuestos: {factura['impuestos']}")
                print(f" Descuentos: {factura['descuentos']}")
                print(f" Total: {factura['total_factura']}")
                print(f" Estado: {factura['estado_factura']}")
                print(f" Observaciones: {factura['observaciones']}")
                
                # 5. Probar registro de pago
                print("\n5. Probando registro de pago...")
                
                pago_data = {
                    "id_factura": factura['id_factura'],
                    "id_metodo_pago": 1,
                    "id_tipo_pago": 2,
                    "fecha_pago": str(date.today()),
                    "valor": 50000.00
                }
                
                pago_response = requests.post(
                    f"{BASE_URL}/api/pagos/registrar",
                    json=pago_data,
                    headers=headers
                )
                
                print(f"Status Code: {pago_response.status_code}")
                print(f"Respuesta: {pago_response.text}")
                
                if pago_response.status_code == 201:
                    print(" Pago registrado exitosamente")
                else:
                    print(" Error al registrar pago")
            else:
                print(" Error al crear factura")
        else:
            print(" Error al crear contrato")
            
    except Exception as e:
        print(f" Error en prueba: {e}")

    print("\n Pruebas de facturación completa finalizadas")

if __name__ == "__main__":
    test_facturacion_completa() 