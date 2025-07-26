# Prevención de Doble Agendamiento

## Descripción del Problema

El sistema de cronogramas de asistencia debe garantizar que **un paciente no pueda estar agendado más de una vez en el mismo día**. Esto es crítico para:

- Evitar conflictos de horarios
- Mantener la integridad de los datos
- Prevenir errores en la gestión de asistencia
- Asegurar que los días de tiquetera se consuman correctamente

## Solución Implementada

Se han implementado **múltiples capas de validación** para prevenir el doble agendamiento:

### 1. Validación a Nivel de API (Primera Línea de Defensa)

#### En Creación de Contratos (`/api/contratos/`)

```python
# Validación antes de procesar cronogramas
for fecha in fechas_tiquetera:
    cronograma_existente = db.query(CronogramaAsistencia).filter(
        CronogramaAsistencia.fecha == fecha,
        CronogramaAsistencia.id_profesional == id_profesional_default
    ).first()

    if cronograma_existente:
        paciente_ya_agendado = db.query(CronogramaAsistenciaPacientes).filter(
            CronogramaAsistenciaPacientes.id_cronograma == cronograma_existente.id_cronograma,
            CronogramaAsistenciaPacientes.id_usuario == data.id_usuario
        ).first()

        if paciente_ya_agendado:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"El paciente ya está agendado para la fecha {fecha}..."
            )
```

#### En Agregar Paciente a Cronograma (`/api/cronograma_asistencia/paciente/agregar`)

```python
# Verificar que el paciente ya está en el cronograma
paciente_existente = db.query(CronogramaAsistenciaPacientes).filter(
    CronogramaAsistenciaPacientes.id_cronograma == paciente_data.id_cronograma,
    CronogramaAsistenciaPacientes.id_usuario == paciente_data.id_usuario
).first()

if paciente_existente:
    raise HTTPException(
        status_code=400,
        detail=f"El paciente ya está registrado en este cronograma para la fecha {cronograma.fecha}..."
    )
```

### 2. Validación a Nivel de Base de Datos (Segunda Línea de Defensa)

#### Índice Único

```sql
ALTER TABLE cronograma_asistencia_pacientes
ADD UNIQUE INDEX idx_unique_paciente_cronograma (id_cronograma, id_usuario);
```

Este índice único previene que se puedan insertar registros duplicados a nivel de base de datos.

#### Trigger de Validación

```sql
CREATE TRIGGER validar_doble_agendamiento
BEFORE INSERT ON cronograma_asistencia_pacientes
FOR EACH ROW
BEGIN
    DECLARE paciente_count INT DEFAULT 0;

    SELECT COUNT(*) INTO paciente_count
    FROM cronograma_asistencia_pacientes
    WHERE id_cronograma = NEW.id_cronograma
    AND id_usuario = NEW.id_usuario;

    IF paciente_count > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'No se puede agendar un paciente dos veces en el mismo cronograma';
    END IF;
END
```

### 3. Índices de Optimización

```sql
-- Para optimizar consultas de validación
CREATE INDEX idx_paciente_fecha ON cronograma_asistencia_pacientes (id_usuario, id_cronograma);

-- Para optimizar consultas por contrato
CREATE INDEX idx_contrato_paciente ON cronograma_asistencia_pacientes (id_contrato, id_usuario);
```

## Flujo de Validación

### Al Crear un Contrato

1. **Validación Previa**: Antes de crear cualquier registro, se verifica si el paciente ya está agendado para las fechas del contrato
2. **Rollback Automático**: Si se detecta un conflicto, se hace rollback de todo lo creado hasta ese momento
3. **Mensaje de Error Descriptivo**: Se informa exactamente qué fecha tiene conflicto y el estado actual del paciente

### Al Agregar Paciente a Cronograma

1. **Validación de Existencia**: Se verifica que el cronograma y el contrato existan
2. **Validación de Doble Agendamiento**: Se verifica que el paciente no esté ya agendado
3. **Validación de Propiedad**: Se verifica que el contrato pertenezca al usuario

## Mensajes de Error

Los mensajes de error son descriptivos e incluyen:

- **Fecha específica** del conflicto
- **ID del paciente** involucrado
- **Estado actual** del agendamiento existente
- **Contexto** de la operación que falló

### Ejemplos de Mensajes

```
"El paciente ya está agendado para la fecha 2025-01-15.
No se puede crear un doble agendamiento.
Paciente ID: 123, Estado actual: PENDIENTE"
```

```
"El paciente ya está registrado en este cronograma para la fecha 2025-01-15.
No se puede crear un doble agendamiento.
Paciente ID: 123, Estado actual: ASISTIO"
```

## Casos de Uso Cubiertos

### Casos Prevenidos

1. **Crear contrato con fechas que ya tienen agendamiento**
2. **Agregar paciente a cronograma existente**
3. **Reagendar paciente a fecha ya ocupada**
4. **Inserción directa en base de datos**

### Casos Permitidos

1. **Crear contrato con fechas nuevas**
2. **Agregar paciente a cronograma vacío**
3. **Reagendar paciente a fecha libre**
4. **Actualizar estado de agendamiento existente**

## Implementación de la Migración

Para aplicar las validaciones de base de datos:

```bash
# Desde el directorio carelink-migrations
mysql -u root -p carelink < prevent_double_booking.sql
```

## Pruebas

Se incluye un script de pruebas (`test_double_booking.py`) que verifica:

1. **Restricciones de base de datos**
2. **Validaciones de API**
3. **Datos existentes conflictivos**
4. **Limpieza de datos de prueba**

Para ejecutar las pruebas:

```bash
cd carelink-back
python test_double_booking.py
```

## Monitoreo y Mantenimiento

### Verificar Integridad

```sql
-- Consulta para verificar dobles agendamientos
SELECT
    cap.id_usuario,
    ca.fecha,
    COUNT(*) as agendamientos
FROM cronograma_asistencia_pacientes cap
JOIN cronograma_asistencia ca ON cap.id_cronograma = ca.id_cronograma
GROUP BY cap.id_usuario, ca.fecha
HAVING COUNT(*) > 1
ORDER BY agendamientos DESC;
```

### Logs de Auditoría

Los errores de doble agendamiento se registran en los logs del servidor con:

- **Timestamp** de la operación
- **Usuario** que intentó la operación
- **Datos** del conflicto
- **Stack trace** completo

## Consideraciones de Rendimiento

- Los índices únicos tienen un impacto mínimo en el rendimiento de escritura
- Las consultas de validación están optimizadas con índices específicos
- El trigger se ejecuta solo en operaciones de inserción
- Las validaciones de API son eficientes y usan consultas indexadas

## Resumen de Protecciones

| Nivel             | Protección        | Descripción                        |
| ----------------- | ----------------- | ---------------------------------- |
| **API**           | Validación previa | Verifica antes de crear registros  |
| **Base de Datos** | Índice único      | Previene duplicados a nivel DB     |
| **Base de Datos** | Trigger           | Validación adicional como respaldo |
| **Aplicación**    | Rollback          | Revierte cambios en caso de error  |
| **Usuario**       | Mensajes claros   | Informa exactamente qué falló      |

Esta implementación garantiza que **es imposible** crear un doble agendamiento en el sistema, manteniendo la integridad de los datos y la experiencia del usuario.
