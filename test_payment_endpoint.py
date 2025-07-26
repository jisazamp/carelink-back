#!/usr/bin/env python3
"""
Script de prueba para verificar el endpoint de pagos
"""

import requests
import json
from datetime import date

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
PAYMENT_URL = f"{BASE_URL}/api/pagos/registrar"

def test_payment_endpoint():
    """Prueba el endpoint de registro de pagos"""
    
    print(" Iniciando pruebas del endpoint de pagos...")
    
    # 1. Login para obtener token
    print("\n1. Obteniendo token de autenticación...")
    login_data = {
        "email": "admin@carelink.com",
        "password": "admin123"
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

    # 2. Probar registro de pago válido
    print("\n2. Probando registro de pago válido...")
    valid_payment = {
        "id_factura": 1,
        "id_metodo_pago": 1,
        "id_tipo_pago": 2,  # Pago parcial
        "fecha_pago": str(date.today()),
        "valor": 100000.00
    }
    
    try:
        payment_response = requests.post(PAYMENT_URL, json=valid_payment, headers=headers)
        print(f"Status Code: {payment_response.status_code}")
        print(f"Respuesta: {payment_response.text}")
        
        if payment_response.status_code == 201:
            print(" Pago registrado exitosamente")
        else:
            print(" Error al registrar pago")
            
    except Exception as e:
        print(f" Error en prueba de pago: {str(e)}")

    # 3. Probar con factura inexistente
    print("\n3. Probando con factura inexistente...")
    invalid_factura_payment = {
        "id_factura": 99999,
        "id_metodo_pago": 1,
        "id_tipo_pago": 2,
        "fecha_pago": str(date.today()),
        "valor": 100000.00
    }
    
    try:
        response = requests.post(PAYMENT_URL, json=invalid_factura_payment, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
        if response.status_code == 400:
            print(" Validación de factura inexistente funciona correctamente")
        else:
            print(" No se validó correctamente la factura inexistente")
            
    except Exception as e:
        print(f" Error en prueba: {str(e)}")

    # 4. Probar con método de pago inexistente
    print("\n4. Probando con método de pago inexistente...")
    invalid_method_payment = {
        "id_factura": 1,
        "id_metodo_pago": 99999,
        "id_tipo_pago": 2,
        "fecha_pago": str(date.today()),
        "valor": 100000.00
    }
    
    try:
        response = requests.post(PAYMENT_URL, json=invalid_method_payment, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
        if response.status_code == 400:
            print(" Validación de método de pago inexistente funciona correctamente")
        else:
            print(" No se validó correctamente el método de pago inexistente")
            
    except Exception as e:
        print(f" Error en prueba: {str(e)}")

    # 5. Probar con tipo de pago inexistente
    print("\n5. Probando con tipo de pago inexistente...")
    invalid_type_payment = {
        "id_factura": 1,
        "id_metodo_pago": 1,
        "id_tipo_pago": 99999,
        "fecha_pago": str(date.today()),
        "valor": 100000.00
    }
    
    try:
        response = requests.post(PAYMENT_URL, json=invalid_type_payment, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Respuesta: {response.text}")
        
        if response.status_code == 400:
            print(" Validación de tipo de pago inexistente funciona correctamente")
        else:
            print(" No se validó correctamente el tipo de pago inexistente")
            
    except Exception as e:
        print(f" Error en prueba: {str(e)}")

    print("\n Pruebas completadas")

if __name__ == "__main__":
    test_payment_endpoint() 