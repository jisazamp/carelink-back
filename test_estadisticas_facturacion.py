#!/usr/bin/env python3
"""
Script de prueba para verificar las estadísticas de facturación
"""

import requests
import json
from datetime import date

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login"
FACTURAS_URL = f"{BASE_URL}/api/facturas"
ESTADISTICAS_URL = f"{BASE_URL}/api/facturas/estadisticas"

def test_estadisticas_facturacion():
    """Prueba las estadísticas de facturación"""
    
    print("🧪 Iniciando pruebas de estadísticas de facturación...")
    
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

    # 2. Obtener todas las facturas
    print("\n2. Obteniendo todas las facturas...")
    
    try:
        facturas_response = requests.get(FACTURAS_URL, headers=headers)
        print(f"Status Code: {facturas_response.status_code}")
        
        if facturas_response.status_code == 200:
            facturas = facturas_response.json()["data"]
            print(f" Facturas obtenidas: {len(facturas)}")
            
            # Mostrar información de cada factura
            for factura in facturas:
                print(f"  - Factura #{factura['id_factura']}: ${factura['total_factura']} - {factura['estado_factura']}")
                if factura.get('pagos'):
                    total_pagado = sum(pago['valor'] for pago in factura['pagos'])
                    print(f"    Pagos: {len(factura['pagos'])} - Total pagado: ${total_pagado}")
                else:
                    print(f"    Sin pagos registrados")
        else:
            print(" Error al obtener facturas")
            
    except Exception as e:
        print(f" Error al obtener facturas: {e}")

    # 3. Obtener estadísticas
    print("\n3. Obteniendo estadísticas de facturación...")
    
    try:
        estadisticas_response = requests.get(ESTADISTICAS_URL, headers=headers)
        print(f"Status Code: {estadisticas_response.status_code}")
        
        if estadisticas_response.status_code == 200:
            estadisticas = estadisticas_response.json()
            print(" Estadísticas obtenidas:")
            print(f"  - Total facturas: {estadisticas['total']}")
            print(f"  - Pagadas: {estadisticas['pagadas']}")
            print(f"  - Pendientes: {estadisticas['pendientes']}")
            print(f"  - Vencidas: {estadisticas['vencidas']}")
            print(f"  - Canceladas: {estadisticas['canceladas']}")
            print(f"  - Anuladas: {estadisticas['anuladas']}")
            print(f"  - Valor total: ${estadisticas['totalValor']:,.0f}")
            print(f"  - Valor pagado: ${estadisticas['valorPagado']:,.0f}")
            print(f"  - Valor pendiente: ${estadisticas['valorPendiente']:,.0f}")
            
            # Verificar cálculos
            total_calculado = estadisticas['pagadas'] + estadisticas['pendientes'] + estadisticas['vencidas'] + estadisticas['canceladas'] + estadisticas['anuladas']
            if total_calculado == estadisticas['total']:
                print(" Verificación de totales: CORRECTO")
            else:
                print(f" Error en totales: {total_calculado} vs {estadisticas['total']}")
            
            valor_calculado = estadisticas['valorPagado'] + estadisticas['valorPendiente']
            if abs(valor_calculado - estadisticas['totalValor']) < 1:  # Tolerancia para decimales
                print(" Verificación de valores: CORRECTO")
            else:
                print(f" Error en valores: {valor_calculado} vs {estadisticas['totalValor']}")
                
        else:
            print(" Error al obtener estadísticas")
            print(f"Respuesta: {estadisticas_response.text}")
            
    except Exception as e:
        print(f" Error al obtener estadísticas: {e}")

    # 4. Verificar consistencia entre facturas y estadísticas
    print("\n4. Verificando consistencia...")
    
    try:
        # Recalcular estadísticas manualmente
        facturas_response = requests.get(FACTURAS_URL, headers=headers)
        if facturas_response.status_code == 200:
            facturas = facturas_response.json()["data"]
            
            total_manual = len(facturas)
            pagadas_manual = sum(1 for f in facturas if f['estado_factura'] == 'PAGADA')
            pendientes_manual = sum(1 for f in facturas if f['estado_factura'] == 'PENDIENTE')
            vencidas_manual = sum(1 for f in facturas if f['estado_factura'] == 'VENCIDA')
            canceladas_manual = sum(1 for f in facturas if f['estado_factura'] == 'CANCELADA')
            anuladas_manual = sum(1 for f in facturas if f['estado_factura'] == 'ANULADA')
            
            total_valor_manual = sum(f['total_factura'] for f in facturas)
            valor_pendiente_manual = 0
            
            for factura in facturas:
                total_factura = factura['total_factura']
                total_pagado = sum(pago['valor'] for pago in factura.get('pagos', []))
                valor_pendiente_manual += max(0, total_factura - total_pagado)
            
            print("📊 Comparación manual vs backend:")
            print(f"  Total: {total_manual} vs {estadisticas['total']}")
            print(f"  Pagadas: {pagadas_manual} vs {estadisticas['pagadas']}")
            print(f"  Pendientes: {pendientes_manual} vs {estadisticas['pendientes']}")
            print(f"  Vencidas: {vencidas_manual} vs {estadisticas['vencidas']}")
            print(f"  Valor total: ${total_valor_manual:,.0f} vs ${estadisticas['totalValor']:,.0f}")
            print(f"  Valor pendiente: ${valor_pendiente_manual:,.0f} vs ${estadisticas['valorPendiente']:,.0f}")
            
    except Exception as e:
        print(f" Error en verificación de consistencia: {e}")

    print("\n Pruebas de estadísticas completadas")

if __name__ == "__main__":
    test_estadisticas_facturacion() 