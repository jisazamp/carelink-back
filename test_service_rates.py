#!/usr/bin/env python3
"""
Script de prueba para verificar los endpoints de tarifas de servicios
"""

import requests
import json
from datetime import date

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
GET_RATES_URL = f"{BASE_URL}/api/tarifas-servicios"
UPDATE_RATES_URL = f"{BASE_URL}/api/tarifas-servicios"

def test_service_rates_endpoints():
    """Prueba los endpoints de tarifas de servicios"""
    
    print(" Iniciando pruebas de tarifas de servicios...")
    
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
        print(f" Error en login: {e}")
        return

    # 2. Obtener tarifas actuales
    print("\n2. Obteniendo tarifas actuales...")
    
    try:
        get_response = requests.get(GET_RATES_URL, headers=headers)
        print(f"Status Code: {get_response.status_code}")
        print(f"Respuesta: {get_response.text}")
        
        if get_response.status_code == 200:
            rates_data = get_response.json()
            print(" Tarifas obtenidas exitosamente")
            print(f" Número de tarifas: {len(rates_data.get('data', {}).get('TarifasServicioPorAnio', []))}")
        else:
            print(" Error al obtener tarifas")
            return
            
    except Exception as e:
        print(f" Error al obtener tarifas: {e}")
        return

    # 3. Actualizar tarifas
    print("\n3. Actualizando tarifas...")
    
    # Datos de prueba para actualizar
    update_data = {
        "TarifasServicioPorAnio": [
            {
                "id": 1,
                "id_servicio": 1,
                "anio": 2025,
                "precio_por_dia": 90000.00
            },
            {
                "id": 2,
                "id_servicio": 2,
                "anio": 2025,
                "precio_por_dia": 60000.00
            },
            {
                "id": 3,
                "id_servicio": 3,
                "anio": 2025,
                "precio_por_dia": 40000.00
            }
        ]
    }
    
    try:
        update_response = requests.patch(UPDATE_RATES_URL, json=update_data, headers=headers)
        print(f"Status Code: {update_response.status_code}")
        print(f"Respuesta: {update_response.text}")
        
        if update_response.status_code == 200:
            print(" Tarifas actualizadas exitosamente")
        else:
            print(" Error al actualizar tarifas")
            
    except Exception as e:
        print(f" Error al actualizar tarifas: {e}")

    # 4. Verificar tarifas actualizadas
    print("\n4. Verificando tarifas actualizadas...")
    
    try:
        verify_response = requests.get(GET_RATES_URL, headers=headers)
        print(f"Status Code: {verify_response.status_code}")
        
        if verify_response.status_code == 200:
            updated_rates = verify_response.json()
            print(" Tarifas verificadas después de actualización")
            for rate in updated_rates.get('data', {}).get('TarifasServicioPorAnio', []):
                print(f"  - Servicio {rate['id_servicio']}: ${rate['precio_por_dia']:,.2f}")
        else:
            print(" Error al verificar tarifas actualizadas")
            
    except Exception as e:
        print(f" Error en verificación: {e}")

    print("\n Pruebas de tarifas de servicios completadas")

if __name__ == "__main__":
    test_service_rates_endpoints() 