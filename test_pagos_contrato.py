#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo completo de creación de contrato, factura y pagos
"""

import requests
import json
from datetime import date, timedelta

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
CONTRACTS_URL = f"{BASE_URL}/api/contratos/"
BILLS_URL = f"{BASE_URL}/api/facturas"
PAYMENTS_URL = f"{BASE_URL}/api/facturas"

def test_complete_flow():
    """Prueba el flujo completo: contrato -> factura -> pagos"""
    
    print("🧪 Iniciando prueba del flujo completo...")
    
    # 1. Login para obtener token
    print("\n1. Obteniendo token de autenticación...")
    login_data = {
        "email": "davidrestrepover@gmail.com",
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
        print(f" Error en login: {str(e)}")
        return

    # 2. Crear contrato
    print("\n2. Creando contrato...")
    contract_data = {
        "id_usuario": 1,
        "tipo_contrato": "Nuevo",
        "fecha_inicio": str(date.today()),
        "fecha_fin": str(date.today() + timedelta(days=30)),
        "facturar_contrato": True,
        "servicios": [
            {
                "id_servicio": 1,
                "fecha": str(date.today()),
                "descripcion": "Servicio de cuidado básico",
                "precio_por_dia": 50000.0,
                "fechas_servicio": [
                    {"fecha": str(date.today())},
                    {"fecha": str(date.today() + timedelta(days=1))}
                ]
            }
        ],
        "impuestos": 0,
        "descuentos": 0
    }
    
    try:
        contract_response = requests.post(CONTRACTS_URL, json=contract_data, headers=headers)
        print(f"Status Code: {contract_response.status_code}")
        print(f"Respuesta: {contract_response.text}")
        
        if contract_response.status_code == 201:
            contract = contract_response.json()["data"]["data"]
            contract_id = contract["id_contrato"]
            print(f" Contrato creado con ID: {contract_id}")
        else:
            print(" Error al crear contrato")
            return
            
    except Exception as e:
        print(f" Error en creación de contrato: {str(e)}")
        return

    # 3. Crear factura para el contrato
    print("\n3. Creando factura para el contrato...")
    bill_data = {
        "impuestos": 0,
        "descuentos": 0,
        "observaciones": "Factura generada automáticamente desde el contrato"
    }
    
    try:
        bill_response = requests.post(f"{BILLS_URL}/{contract_id}", json=bill_data, headers=headers)
        print(f"Status Code: {bill_response.status_code}")
        print(f"Respuesta: {bill_response.text}")
        
        if bill_response.status_code == 201:
            bill = bill_response.json()["data"]["data"]
            factura_id = bill["id_factura"]
            print(f" Factura creada con ID: {factura_id}")
            print(f" Total factura: {bill['total_factura']}")
        else:
            print(" Error al crear factura")
            return
            
    except Exception as e:
        print(f" Error en creación de factura: {str(e)}")
        return

    # 4. Registrar pagos en la factura
    print("\n4. Registrando pagos en la factura...")
    payments_data = [
        {
            "id_metodo_pago": 1,  # Efectivo
            "id_tipo_pago": 2,    # Pago Parcial
            "fecha_pago": str(date.today()),
            "valor": 50000.0
        },
        {
            "id_metodo_pago": 2,  # Tarjeta de Crédito
            "id_tipo_pago": 2,    # Pago Parcial
            "fecha_pago": str(date.today()),
            "valor": 30000.0
        }
    ]
    
    try:
        payments_response = requests.post(f"{PAYMENTS_URL}/{factura_id}/pagos/", json=payments_data, headers=headers)
        print(f"Status Code: {payments_response.status_code}")
        print(f"Respuesta: {payments_response.text}")
        
        if payments_response.status_code == 201:
            print(" Pagos registrados exitosamente")
        else:
            print(" Error al registrar pagos")
            
    except Exception as e:
        print(f" Error en registro de pagos: {str(e)}")

    # 5. Verificar pagos registrados
    print("\n5. Verificando pagos registrados...")
    try:
        verify_response = requests.get(f"{PAYMENTS_URL}/{factura_id}/pagos/", headers=headers)
        print(f"Status Code: {verify_response.status_code}")
        print(f"Respuesta: {verify_response.text}")
        
        if verify_response.status_code == 200:
            payments = verify_response.json()
            print(f" Pagos encontrados: {len(payments)}")
            for payment in payments:
                print(f"  - Pago ID: {payment['id_pago']}, Valor: {payment['valor']}")
        else:
            print(" Error al verificar pagos")
            
    except Exception as e:
        print(f" Error en verificación de pagos: {str(e)}")

    print("\n Prueba del flujo completo finalizada")

if __name__ == "__main__":
    test_complete_flow() 