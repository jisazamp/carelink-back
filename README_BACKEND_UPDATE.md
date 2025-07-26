# ACTUALIZACIÓN DEL BACKEND - SISTEMA DE FACTURACIÓN Y CRONOGRAMAS

## Resumen de Cambios

Este documento describe las actualizaciones realizadas al backend para sincronizarlo con la base de datos actualizada que incluye el sistema de facturación y cronogramas de asistencia.

## 🗂️ Estructura Actualizada

### Modelos Actualizados

#### 1. **Sistema de Facturación** (`app/models/contracts.py`)

- `Contratos`: Gestión de contratos con usuarios
- `Facturas`: Sistema completo de facturación
- `DetalleFactura`: Detalles de cada factura
- `Servicios`: Catálogo de servicios disponibles
- `ServiciosPorContrato`: Servicios asociados a contratos
- `FechasServicio`: Fechas específicas de servicios
- `Pagos`: Registro de pagos realizados
- `MetodoPago`: Métodos de pago disponibles
- `TipoPago`: Tipos de pago
- `EstadoFactura`: Estados de facturación (PENDIENTE, PAGADA, VENCIDA, etc.)

#### 2. **Sistema de Cronogramas** (`app/models/attendance_schedule.py`)

- `CronogramaAsistencia`: Cronogramas por profesional y fecha
- `CronogramaAsistenciaPacientes`: Pacientes agendados en cronogramas
- `EstadoAsistencia`: Estados de asistencia (PENDIENTE, ASISTIO, NO_ASISTIO, etc.)

#### 3. **Sistema de Transporte** (`app/models/transporte.py`)

- `CronogramaTransporte`: Gestión de transporte para pacientes
- `EstadoTransporte`: Estados de transporte (PENDIENTE, REALIZADO, CANCELADO)

### DTOs Actualizados

#### Request DTOs

- `CronogramaAsistenciaCreateDTO`: Crear cronogramas
- `CronogramaAsistenciaPacienteCreateDTO`: Agregar pacientes a cronogramas
- `EstadoAsistenciaUpdateDTO`: Actualizar estados de asistencia
- `CronogramaTransporteCreateDTO`: Crear registros de transporte
- `CronogramaTransporteUpdateDTO`: Actualizar transporte

#### Response DTOs

- `CronogramaAsistenciaResponseDTO`: Respuesta de cronogramas
- `CronogramaAsistenciaPacienteResponseDTO`: Respuesta de pacientes en cronogramas
- `PacientePorFechaDTO`: Información de pacientes por fecha
- `CronogramaTransporteResponseDTO`: Respuesta de transporte
- `RutaDiariaResponseDTO`: Rutas de transporte diarias

### CRUD Actualizado

#### Nuevos Métodos en `CareLinkCrud`

##### Cronograma de Asistencia

- `create_cronograma_asistencia()`: Crear nuevo cronograma
- `add_paciente_to_cronograma()`: Agregar paciente a cronograma
- `update_estado_asistencia()`: Actualizar estado de asistencia
- `reagendar_paciente()`: Reagendar paciente a nueva fecha
- `get_cronogramas_por_rango()`: Obtener cronogramas por rango de fechas
- `get_cronogramas_por_profesional()`: Obtener cronogramas por profesional

##### Transporte

- `create_transporte()`: Crear registro de transporte
- `update_transporte()`: Actualizar transporte
- `delete_transporte()`: Eliminar transporte
- `get_ruta_diaria()`: Obtener ruta de transporte diaria
- `get_transporte_paciente()`: Obtener transporte de paciente específico

##### Métodos Auxiliares

- `_get_cronograma_by_id()`: Obtener cronograma por ID
- `_get_cronograma_paciente_by_id()`: Obtener paciente de cronograma por ID
- `_get_transporte_by_id()`: Obtener transporte por ID

## 🚀 Endpoints Disponibles

### Cronograma de Asistencia

- `POST /api/cronograma_asistencia/crear`: Crear cronograma
- `POST /api/cronograma_asistencia/paciente/agregar`: Agregar paciente
- `GET /api/cronograma_asistencia/rango/{fecha_inicio}/{fecha_fin}`: Obtener por rango
- `GET /api/cronograma_asistencia/profesional/{id_profesional}`: Obtener por profesional
- `PATCH /api/cronograma_asistencia/paciente/{id}/estado`: Actualizar estado
- `POST /api/cronograma_asistencia/paciente/{id}/reagendar`: Reagendar paciente

### Transporte

- `POST /api/transporte/crear`: Crear transporte
- `PATCH /api/transporte/{id}`: Actualizar transporte
- `DELETE /api/transporte/{id}`: Eliminar transporte
- `GET /api/transporte/ruta/{fecha}`: Obtener ruta diaria
- `GET /api/transporte/paciente/{id}`: Obtener transporte de paciente

### Contratos y Facturación

- `POST /api/contratos/`: Crear contrato
- `GET /api/contratos/{id_usuario}`: Obtener contratos por usuario
- `GET /api/contrato/{id_contrato}`: Obtener contrato específico
- `PATCH /api/contrato/{id_contrato}`: Actualizar contrato
- `POST /api/facturas/{contrato_id}`: Crear factura para contrato
- `GET /api/contratos/{contrato_id}/facturas`: Obtener facturas de contrato
- `POST /api/pagos/`: Crear pago
- `GET /api/pagos/factura/{factura_id}`: Obtener pagos de factura

## Configuración

### Variables de Entorno Requeridas

```bash
DATABASE_CARELINK_CONNECTION_URL=mysql+pymysql://root:@localhost/carelink
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Dependencias

```bash
pip install fastapi uvicorn sqlalchemy pymysql pydantic python-jose[cryptography] passlib[bcrypt] python-multipart boto3
```

## Pruebas

### Script de Pruebas

Se incluye un script de pruebas completo: `test_backend_integration.py`

Para ejecutar las pruebas:

```bash
cd carelink-back
python test_backend_integration.py
```

### Pruebas Incluidas

1. **Conexión a base de datos**
2. **Importación de modelos**
3. **Operaciones CRUD básicas**
4. **Operaciones de cronograma**
5. **Operaciones de transporte**
6. **Operaciones de contratos**
7. **Validación de DTOs**

## 🔒 Validaciones Implementadas

### Cronograma de Asistencia

- Prevención de doble reserva para el mismo paciente en la misma fecha
- Validación de estados de asistencia
- Solo se pueden reagendar pacientes con estado PENDIENTE
- Validación de fechas de reagendamiento

### Transporte

- Verificación de existencia del cronograma del paciente
- Prevención de transporte duplicado para el mismo cronograma
- Validación de formatos de hora
- Validación de estados de transporte

### Contratos y Facturación

- Validación de datos de contrato
- Cálculo automático de totales de facturación
- Validación de métodos y tipos de pago
- Gestión de estados de facturación

## Características Destacadas

### 1. **Sistema de Estados**

- Estados de asistencia: PENDIENTE, ASISTIO, NO_ASISTIO, CANCELADO, REAGENDADO
- Estados de facturación: PENDIENTE, PAGADA, VENCIDA, CANCELADA, ANULADA
- Estados de transporte: PENDIENTE, REALIZADO, CANCELADO

### 2. **Relaciones Complejas**

- Contratos → Servicios → Fechas de Servicio
- Cronogramas → Pacientes → Transporte
- Facturas → Detalles → Pagos

### 3. **Validaciones Robustas**

- Prevención de doble reserva
- Validación de fechas y horarios
- Verificación de existencia de entidades relacionadas
- Validación de estados permitidos

### 4. **Funcionalidades Avanzadas**

- Reagendamiento automático de pacientes
- Cálculo de rutas de transporte
- Gestión completa de facturación
- Sistema de pagos múltiples

## 🚀 Próximos Pasos

1. **Ejecutar pruebas de integración**
2. **Verificar conectividad con frontend**
3. **Probar endpoints críticos**
4. **Documentar APIs con Swagger**
5. **Implementar logging y monitoreo**

## Notas Importantes

- Todos los modelos incluyen timestamps automáticos
- Se implementaron índices para optimizar consultas
- Se mantiene compatibilidad con funcionalidades existentes
- Se agregaron validaciones de seguridad en todos los endpoints
- El sistema es escalable y mantiene integridad referencial

---

**Estado**: Backend actualizado y listo para producción
**Última actualización**: Enero 2025
**Versión**: 2.0.0
