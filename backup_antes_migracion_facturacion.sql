-- ============================================================================
-- RESPALDO ANTES DE MIGRACIÓN DE FACTURACIÓN
-- ============================================================================
-- Fecha: 2025-01-XX
-- Descripción: Respaldo de las tablas de facturación antes de aplicar mejoras
-- Objetivo: Preservar datos existentes en caso de necesidad de rollback

-- ============================================================================
-- 1. CREAR TABLAS DE RESPALDO
-- ============================================================================

-- Respaldo de Facturas
CREATE TABLE `Facturas_BACKUP_$(date +%Y%m%d_%H%M%S)` AS
SELECT *
FROM `Facturas`;

-- Respaldo de DetalleFactura
CREATE TABLE `DetalleFactura_BACKUP_$(date +%Y%m%d_%H%M%S)` AS
SELECT *
FROM `DetalleFactura`;

-- Respaldo de Pagos
CREATE TABLE `Pagos_BACKUP_$(date +%Y%m%d_%H%M%S)` AS
SELECT *
FROM `Pagos`;

-- Respaldo de ServiciosPorContrato
CREATE TABLE `ServiciosPorContrato_BACKUP_$(date +%Y%m%d_%H%M%S)` AS
SELECT *
FROM `ServiciosPorContrato`;

-- Respaldo de MetodoPago
CREATE TABLE `MetodoPago_BACKUP_$(date +%Y%m%d_%H%M%S)` AS
SELECT *
FROM `MetodoPago`;

-- Respaldo de TipoPago
CREATE TABLE `TipoPago_BACKUP_$(date +%Y%m%d_%H%M%S)` AS
SELECT *
FROM `TipoPago`;

-- ============================================================================
-- 2. VERIFICAR INTEGRIDAD DE DATOS
-- ============================================================================

-- Verificar que no hay facturas huérfanas (sin contrato)
SELECT 'Facturas sin contrato' as tipo, COUNT(*) as cantidad
FROM `Facturas` f
    LEFT JOIN `Contratos` c ON f.id_contrato = c.id_contrato
WHERE
    c.id_contrato IS NULL;

-- Verificar que no hay detalles de factura huérfanos (sin factura)
SELECT 'Detalles sin factura' as tipo, COUNT(*) as cantidad
FROM
    `DetalleFactura` df
    LEFT JOIN `Facturas` f ON df.id_factura = f.id_factura
WHERE
    f.id_factura IS NULL;

-- Verificar que no hay pagos huérfanos (sin factura)
SELECT 'Pagos sin factura' as tipo, COUNT(*) as cantidad
FROM `Pagos` p
    LEFT JOIN `Facturas` f ON p.id_factura = f.id_factura
WHERE
    f.id_factura IS NULL;

-- Verificar que no hay servicios por contrato huérfanos (sin contrato)
SELECT 'Servicios sin contrato' as tipo, COUNT(*) as cantidad
FROM
    `ServiciosPorContrato` spc
    LEFT JOIN `Contratos` c ON spc.id_contrato = c.id_contrato
WHERE
    c.id_contrato IS NULL;

-- ============================================================================
-- 3. ESTADÍSTICAS DE DATOS EXISTENTES
-- ============================================================================

-- Estadísticas generales
SELECT
    'Estadísticas de respaldo' as seccion,
    (
        SELECT COUNT(*)
        FROM `Facturas`
    ) as total_facturas,
    (
        SELECT COUNT(*)
        FROM `DetalleFactura`
    ) as total_detalles,
    (
        SELECT COUNT(*)
        FROM `Pagos`
    ) as total_pagos,
    (
        SELECT COUNT(*)
        FROM `ServiciosPorContrato`
    ) as total_servicios_contrato,
    (
        SELECT COUNT(*)
        FROM `MetodoPago`
    ) as total_metodos_pago,
    (
        SELECT COUNT(*)
        FROM `TipoPago`
    ) as total_tipos_pago;

-- ============================================================================
-- 4. COMENTARIOS DE DOCUMENTACIÓN
-- ============================================================================

/*
RESPALDO COMPLETO DEL SISTEMA DE FACTURACIÓN

Este script crea respaldos completos de todas las tablas relacionadas con facturación
antes de aplicar la migración de mejoras.

TABLAS RESPALDADAS:
- Facturas: Facturas principales del sistema
- DetalleFactura: Detalles de cada factura
- Pagos: Pagos asociados a las facturas
- ServiciosPorContrato: Servicios contratados
- MetodoPago: Métodos de pago disponibles
- TipoPago: Tipos de pago disponibles

VERIFICACIONES REALIZADAS:
- Integridad referencial entre tablas
- Detección de registros huérfanos
- Estadísticas de datos existentes

INSTRUCCIONES PARA RESTAURACIÓN (en caso de emergencia):
1. Detener la aplicación
2. Ejecutar: DROP TABLE [tabla_actual];
3. Ejecutar: RENAME TABLE [tabla_backup] TO [tabla_actual];
4. Reiniciar la aplicación

NOTA: Los respaldos se crean con timestamp para evitar conflictos
y permitir múltiples respaldos si es necesario.
*/