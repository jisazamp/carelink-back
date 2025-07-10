#!/usr/bin/env python3
"""
Script de prueba para verificar pagos parciales
"""

import requests
import json
from datetime import date

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
PAYMENT_URL = f"{BASE_URL}/api/pagos/registrar"

def test_partial_payment():
    """Prueba el registro de pagos parciales"""
    
    print("🧪 Iniciando pruebas de pagos parciales...")
    
    # 1. Login para obtener token
    print("\n1. Obteniendo token de autenticación...")
    login_data = {
        "email": "admin@carelink.com",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(LOGIN_URL, json=login_data)
        if login_response.status_code != 200:
            print(f"❌ Error en login: {login_response.status_code}")
            print(f"Respuesta: {login_response.text}")
            return
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login exitoso")
        
    except Exception as e:
        print(f"❌ Error en login: {e}")
        return

    # 2. Probar pago parcial (menor al total de la factura)
    print("\n2. Probando pago parcial...")
    
    # Datos de pago parcial
    partial_payment_data = {
        "id_factura": 1,  # Asegúrate de que esta factura existe
        "id_metodo_pago": 1,  # Efectivo
        "id_tipo_pago": 1,  # Pago Total (pero con valor menor)
        "fecha_pago": str(date.today()),
        "valor": 50000.00  # Valor menor al total de la factura
    }
    
    try:
        payment_response = requests.post(
            PAYMENT_URL, 
            json=partial_payment_data,
            headers=headers
        )
        
        print(f"Status Code: {payment_response.status_code}")
        print(f"Respuesta: {payment_response.text}")
        
        if payment_response.status_code == 201:
            print("✅ Pago parcial registrado exitosamente")
        else:
            print("❌ Error al registrar pago parcial")
            
    except Exception as e:
        print(f"❌ Error en pago parcial: {e}")

    # 3. Probar pago adicional (para completar la factura)
    print("\n3. Probando pago adicional...")
    
    additional_payment_data = {
        "id_factura": 1,  # Misma factura
        "id_metodo_pago": 2,  # Tarjeta de Crédito
        "id_tipo_pago": 2,  # Pago Parcial
        "fecha_pago": str(date.today()),
        "valor": 30000.00  # Valor adicional
    }
    
    try:
        payment_response = requests.post(
            PAYMENT_URL, 
            json=additional_payment_data,
            headers=headers
        )
        
        print(f"Status Code: {payment_response.status_code}")
        print(f"Respuesta: {payment_response.text}")
        
        if payment_response.status_code == 201:
            print("✅ Pago adicional registrado exitosamente")
        else:
            print("❌ Error al registrar pago adicional")
            
    except Exception as e:
        print(f"❌ Error en pago adicional: {e}")

    # 4. Probar pago que excede el total (debe fallar)
    print("\n4. Probando pago que excede el total (debe fallar)...")
    
    excessive_payment_data = {
        "id_factura": 1,  # Misma factura
        "id_metodo_pago": 1,  # Efectivo
        "id_tipo_pago": 2,  # Pago Parcial
        "fecha_pago": str(date.today()),
        "valor": 200000.00  # Valor muy alto
    }
    
    try:
        payment_response = requests.post(
            PAYMENT_URL, 
            json=excessive_payment_data,
            headers=headers
        )
        
        print(f"Status Code: {payment_response.status_code}")
        print(f"Respuesta: {payment_response.text}")
        
        if payment_response.status_code == 400:
            print("✅ Correctamente rechazó pago que excede el total")
        else:
            print("❌ Debería haber rechazado el pago excesivo")
            
    except Exception as e:
        print(f"❌ Error en pago excesivo: {e}")

if __name__ == "__main__":
    test_partial_payment()
    print("\n✅ Pruebas de pagos parciales completadas") 