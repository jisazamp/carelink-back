# 🏷️ Endpoint de Tarifas de Servicios

## 📋 Descripción

Se ha implementado un nuevo sistema para gestionar las tarifas de servicios por año desde el módulo de facturación. Este sistema permite actualizar los precios por día de cada servicio de forma dinámica.

## 🔧 Endpoints Implementados

### **GET /api/tarifas-servicios**

Obtiene todas las tarifas de servicios con información del servicio.

**Respuesta:**

```json
{
  "data": {
    "TarifasServicioPorAnio": [
      {
        "id": 1,
        "id_servicio": 1,
        "anio": 2025,
        "precio_por_dia": 90000.0,
        "nombre_servicio": "Cuidado Básico"
      },
      {
        "id": 2,
        "id_servicio": 2,
        "anio": 2025,
        "precio_por_dia": 60000.0,
        "nombre_servicio": "Cuidado Especializado"
      }
    ]
  },
  "message": "Se obtuvieron 2 tarifas de servicios",
  "success": true
}
```

### **PATCH /api/tarifas-servicios**

Actualiza múltiples tarifas de servicios por año.

**Request Body:**

```json
{
  "TarifasServicioPorAnio": [
    {
      "id": 1,
      "id_servicio": 1,
      "anio": 2025,
      "precio_por_dia": 90000.0
    },
    {
      "id": 2,
      "id_servicio": 2,
      "anio": 2025,
      "precio_por_dia": 60000.0
    },
    {
      "id": 3,
      "id_servicio": 3,
      "anio": 2025,
      "precio_por_dia": 40000.0
    }
  ]
}
```

## 🏗️ Arquitectura Backend

### **DTOs Creados**

- `TarifaServicioUpdateDTO`: Para validar datos de actualización
- `TarifasServicioUpdateRequestDTO`: Para validar el request completo
- `TarifaServicioResponseDTO`: Para respuestas individuales
- `TarifasServicioResponseDTO`: Para respuestas múltiples

### **Métodos CRUD Agregados**

- `get_all_service_rates()`: Obtiene todas las tarifas con información del servicio
- `update_service_rates()`: Actualiza múltiples tarifas con validaciones

### **Validaciones Implementadas**

- Precio por día debe ser mayor a 0
- Año debe estar entre 2020 y 2030
- ID de servicio debe ser válido
- Debe proporcionar al menos una tarifa

## 🎨 Frontend Implementado

### **Hooks Creados**

- `useGetServiceRates`: Para obtener tarifas
- `useUpdateServiceRates`: Para actualizar tarifas

### **Componente Creado**

- `ServiceRatesEditor`: Editor visual para modificar tarifas

### **Características del Editor**

- ✅ Tabla editable con formateo de moneda
- ✅ Validación en tiempo real
- ✅ Indicador de cambios sin guardar
- ✅ Botones de guardar y recargar
- ✅ Manejo de errores y loading states
- ✅ Integración con el módulo de facturación

## 🔗 Integración en Facturación

El editor de tarifas se integra en el módulo de facturación (`/facturacion`) con:

1. **Botón de acceso**: "Mostrar/Ocultar Configuración de Tarifas"
2. **Editor expandible**: Se muestra/oculta según el estado
3. **Formateo consistente**: Usa el mismo formateo de moneda que otros componentes
4. **Validaciones robustas**: Previene datos inválidos

## 🧪 Pruebas

### **Script de Prueba**

- `test_service_rates.py`: Prueba completa de los endpoints
- Verifica login, obtención, actualización y verificación

### **Ejecutar Pruebas**

```bash
cd carelink-back
python test_service_rates.py
```

## 📊 Beneficios

1. **Gestión Dinámica**: Actualizar precios sin reiniciar el sistema
2. **Validación Robusta**: Previene datos incorrectos
3. **UI Intuitiva**: Editor visual fácil de usar
4. **Integración Completa**: Funciona con el flujo de facturación existente
5. **Escalabilidad**: Fácil agregar nuevos servicios o años

## 🚀 Uso

1. **Acceder al módulo**: Ir a `http://localhost:5173/facturacion`
2. **Mostrar editor**: Hacer clic en "Mostrar Configuración de Tarifas"
3. **Editar precios**: Modificar los valores en la tabla
4. **Guardar cambios**: Hacer clic en "Guardar Cambios"
5. **Verificar**: Los cambios se aplican inmediatamente

## 🔒 Seguridad

- ✅ Autenticación requerida en todos los endpoints
- ✅ Validación de datos en frontend y backend
- ✅ Manejo de errores robusto
- ✅ Logs de operaciones para auditoría

---

**Fecha de Implementación**: Julio 2025  
**Responsable**: Sistema de Gestión de Tarifas  
**Estado**: ✅ Completado y Probado
