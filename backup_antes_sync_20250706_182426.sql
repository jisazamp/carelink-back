-- MySQL dump 10.13  Distrib 8.0.42, for Linux (x86_64)
--
-- Host: 127.0.0.1    Database: carelink
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `ActitudPresente`
--

DROP TABLE IF EXISTS `ActitudPresente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ActitudPresente` (
  `id_ActitudPresente` int NOT NULL AUTO_INCREMENT,
  `nom_ActitudPresente` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_ActitudPresente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ActitudPresente`
--

LOCK TABLES `ActitudPresente` WRITE;
/*!40000 ALTER TABLE `ActitudPresente` DISABLE KEYS */;
/*!40000 ALTER TABLE `ActitudPresente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ActitudTemporal`
--

DROP TABLE IF EXISTS `ActitudTemporal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ActitudTemporal` (
  `id_ActitudTemporal` int NOT NULL AUTO_INCREMENT,
  `nom_ActidudTemporal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_ActitudTemporal`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ActitudTemporal`
--

LOCK TABLES `ActitudTemporal` WRITE;
/*!40000 ALTER TABLE `ActitudTemporal` DISABLE KEYS */;
/*!40000 ALTER TABLE `ActitudTemporal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ActividadesGrupales`
--

DROP TABLE IF EXISTS `ActividadesGrupales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ActividadesGrupales` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_profesional` int DEFAULT NULL,
  `id_tipo_actividad` int DEFAULT NULL,
  `comentarios` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `descripcion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `duracion` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `nombre` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_profesional` (`id_profesional`),
  KEY `id_tipo_actividad` (`id_tipo_actividad`),
  CONSTRAINT `ActividadesGrupales_ibfk_1` FOREIGN KEY (`id_profesional`) REFERENCES `Profesionales` (`id_profesional`),
  CONSTRAINT `ActividadesGrupales_ibfk_2` FOREIGN KEY (`id_tipo_actividad`) REFERENCES `TipoActividad` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ActividadesGrupales`
--

LOCK TABLES `ActividadesGrupales` WRITE;
/*!40000 ALTER TABLE `ActividadesGrupales` DISABLE KEYS */;
INSERT INTO `ActividadesGrupales` VALUES (1,1,1,'SE JUEGA TENIS DE MESA','JUGAR TENIS DE MESA',25,'2025-05-06','TENIS DE MESA');
/*!40000 ALTER TABLE `ActividadesGrupales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ApoyosPorUsuario`
--

DROP TABLE IF EXISTS `ApoyosPorUsuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ApoyosPorUsuario` (
  `id_tipoapoyo` int NOT NULL,
  `id_historiaClinica` int NOT NULL,
  `periodicidad` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  PRIMARY KEY (`id_tipoapoyo`,`id_historiaClinica`),
  KEY `id_historiaClinica` (`id_historiaClinica`),
  CONSTRAINT `ApoyosPorUsuario_ibfk_1` FOREIGN KEY (`id_tipoapoyo`) REFERENCES `TipoApoyoTratamientos` (`id_TipoApoyoTratamiento`),
  CONSTRAINT `ApoyosPorUsuario_ibfk_2` FOREIGN KEY (`id_historiaClinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ApoyosPorUsuario`
--

LOCK TABLES `ApoyosPorUsuario` WRITE;
/*!40000 ALTER TABLE `ApoyosPorUsuario` DISABLE KEYS */;
/*!40000 ALTER TABLE `ApoyosPorUsuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `AtencionMemoria`
--

DROP TABLE IF EXISTS `AtencionMemoria`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `AtencionMemoria` (
  `id_AtencionMemoria` int NOT NULL AUTO_INCREMENT,
  `nom_AtencionMemoria` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_AtencionMemoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `AtencionMemoria`
--

LOCK TABLES `AtencionMemoria` WRITE;
/*!40000 ALTER TABLE `AtencionMemoria` DISABLE KEYS */;
/*!40000 ALTER TABLE `AtencionMemoria` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Contratos`
--

DROP TABLE IF EXISTS `Contratos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Contratos` (
  `id_contrato` int NOT NULL AUTO_INCREMENT,
  `id_usuario` int DEFAULT NULL,
  `tipo_contrato` enum('Nuevo','Recurrente') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `facturar_contrato` tinyint(1) DEFAULT '0',
  `estado` enum('ACTIVO','VENCIDO','CANCELADO') COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIVO',
  PRIMARY KEY (`id_contrato`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `Contratos_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `Usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Contratos`
--

LOCK TABLES `Contratos` WRITE;
/*!40000 ALTER TABLE `Contratos` DISABLE KEYS */;
INSERT INTO `Contratos` VALUES (1,1,'Nuevo','2025-07-06','2025-08-06',1,'ACTIVO'),(2,1,'Nuevo','2025-07-07','2025-08-07',1,'ACTIVO'),(3,1,'Nuevo','2025-07-07','2025-08-07',1,'ACTIVO'),(4,1,'Nuevo','2025-07-07','2025-08-07',1,'ACTIVO'),(5,1,'Nuevo','2025-07-07','2025-08-07',1,'ACTIVO'),(6,1,'Nuevo','2025-07-07','2025-08-07',1,'ACTIVO'),(7,2,'Nuevo','2025-07-07','2025-08-07',1,'ACTIVO');
/*!40000 ALTER TABLE `Contratos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `CuidadosEnfermeriaPorUsuario`
--

DROP TABLE IF EXISTS `CuidadosEnfermeriaPorUsuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `CuidadosEnfermeriaPorUsuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_historiaClinica` int DEFAULT NULL,
  `diagnostico` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `frecuencia` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `intervencion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `id_historiaClinica` (`id_historiaClinica`),
  CONSTRAINT `CuidadosEnfermeriaPorUsuario_ibfk_1` FOREIGN KEY (`id_historiaClinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `CuidadosEnfermeriaPorUsuario`
--

LOCK TABLES `CuidadosEnfermeriaPorUsuario` WRITE;
/*!40000 ALTER TABLE `CuidadosEnfermeriaPorUsuario` DISABLE KEYS */;
INSERT INTO `CuidadosEnfermeriaPorUsuario` VALUES (1,1,'Aquí se agrega un diagnóstico','Aquí se agrega la frecuencia de la intervención de acuerdo al diagnóstico','Aquí se agrega una intervención para ese diagnóstico'),(2,2,'UN DIAGNÓSTICO','CADA CUANTO','PRUEBA');
/*!40000 ALTER TABLE `CuidadosEnfermeriaPorUsuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DetalleFactura`
--

DROP TABLE IF EXISTS `DetalleFactura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DetalleFactura` (
  `id_detalle_factura` int NOT NULL AUTO_INCREMENT,
  `id_factura` int DEFAULT NULL,
  `id_servicio_contratado` int DEFAULT NULL,
  `cantidad` int DEFAULT NULL,
  `valor_unitario` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_detalle_factura`),
  KEY `id_factura` (`id_factura`),
  KEY `id_servicio_contratado` (`id_servicio_contratado`),
  CONSTRAINT `DetalleFactura_ibfk_1` FOREIGN KEY (`id_factura`) REFERENCES `Facturas` (`id_factura`) ON DELETE CASCADE,
  CONSTRAINT `DetalleFactura_ibfk_2` FOREIGN KEY (`id_servicio_contratado`) REFERENCES `ServiciosPorContrato` (`id_servicio_contratado`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DetalleFactura`
--

LOCK TABLES `DetalleFactura` WRITE;
/*!40000 ALTER TABLE `DetalleFactura` DISABLE KEYS */;
/*!40000 ALTER TABLE `DetalleFactura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `DocumentoAdjuntoExam`
--

DROP TABLE IF EXISTS `DocumentoAdjuntoExam`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `DocumentoAdjuntoExam` (
  `id_DocumentoAdjunto` int NOT NULL AUTO_INCREMENT,
  `ruta_DocumentoAdjunto` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `nom_DocumentoAdjunto` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `peso_DocumentoAdjunto` float DEFAULT NULL,
  `Tipo_DocumentoAdjunto` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_DocumentoAdjunto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `DocumentoAdjuntoExam`
--

LOCK TABLES `DocumentoAdjuntoExam` WRITE;
/*!40000 ALTER TABLE `DocumentoAdjuntoExam` DISABLE KEYS */;
/*!40000 ALTER TABLE `DocumentoAdjuntoExam` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EsquemaVacunacion`
--

DROP TABLE IF EXISTS `EsquemaVacunacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EsquemaVacunacion` (
  `id_vacuna` int NOT NULL,
  `id_historiaClinica` int NOT NULL,
  `fecha_aplicacion` date DEFAULT NULL,
  PRIMARY KEY (`id_vacuna`,`id_historiaClinica`),
  KEY `id_historiaClinica` (`id_historiaClinica`),
  CONSTRAINT `EsquemaVacunacion_ibfk_1` FOREIGN KEY (`id_vacuna`) REFERENCES `Vacunas` (`id_vacuna`),
  CONSTRAINT `EsquemaVacunacion_ibfk_2` FOREIGN KEY (`id_historiaClinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EsquemaVacunacion`
--

LOCK TABLES `EsquemaVacunacion` WRITE;
/*!40000 ALTER TABLE `EsquemaVacunacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `EsquemaVacunacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `EvolucionesClinicas`
--

DROP TABLE IF EXISTS `EvolucionesClinicas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `EvolucionesClinicas` (
  `id_TipoReporte` int NOT NULL AUTO_INCREMENT,
  `id_reporteclinico` int DEFAULT NULL,
  `id_profesional` int DEFAULT NULL,
  `fecha_evolucion` date DEFAULT NULL,
  `observacion_evolucion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `tipo_report` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_TipoReporte`),
  KEY `id_reporteclinico` (`id_reporteclinico`),
  KEY `id_profesional` (`id_profesional`),
  CONSTRAINT `EvolucionesClinicas_ibfk_1` FOREIGN KEY (`id_reporteclinico`) REFERENCES `ReportesClinicos` (`id_reporteclinico`) ON DELETE CASCADE,
  CONSTRAINT `EvolucionesClinicas_ibfk_2` FOREIGN KEY (`id_profesional`) REFERENCES `Profesionales` (`id_profesional`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `EvolucionesClinicas`
--

LOCK TABLES `EvolucionesClinicas` WRITE;
/*!40000 ALTER TABLE `EvolucionesClinicas` DISABLE KEYS */;
INSERT INTO `EvolucionesClinicas` VALUES (1,4,1,'2025-05-10','OBSERVACIÓNES DE REPORTES DE EVOLUCIÓNES CLÍNICAS','PSICOLOGIA'),(2,4,1,'2025-05-10','Observación 2 prueba','nutricion'),(3,4,1,'2025-05-10','Observación de reporte de evolución clinica','nutricion'),(4,1,1,'2025-06-30','PRUEBA DE CREACIÓN DE NUEVO REPORTE CLÍNICO','psicologia');
/*!40000 ALTER TABLE `EvolucionesClinicas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ExpresionEmosional`
--

DROP TABLE IF EXISTS `ExpresionEmosional`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ExpresionEmosional` (
  `id_expresionemosional` int NOT NULL AUTO_INCREMENT,
  `nom_expresionemocional` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_expresionemosional`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ExpresionEmosional`
--

LOCK TABLES `ExpresionEmosional` WRITE;
/*!40000 ALTER TABLE `ExpresionEmosional` DISABLE KEYS */;
/*!40000 ALTER TABLE `ExpresionEmosional` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Facturas`
--

DROP TABLE IF EXISTS `Facturas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Facturas` (
  `id_factura` int NOT NULL AUTO_INCREMENT,
  `id_contrato` int DEFAULT NULL,
  `fecha_emision` date DEFAULT NULL,
  `total_factura` decimal(10,2) DEFAULT NULL,
  `estado_factura` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_factura`),
  KEY `id_contrato` (`id_contrato`),
  CONSTRAINT `Facturas_ibfk_1` FOREIGN KEY (`id_contrato`) REFERENCES `Contratos` (`id_contrato`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Facturas`
--

LOCK TABLES `Facturas` WRITE;
/*!40000 ALTER TABLE `Facturas` DISABLE KEYS */;
INSERT INTO `Facturas` VALUES (1,1,'2025-07-06',4000000.00,NULL),(2,7,'2025-07-06',800000.00,NULL);
/*!40000 ALTER TABLE `Facturas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Familiares`
--

DROP TABLE IF EXISTS `Familiares`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Familiares` (
  `id_acudiente` int NOT NULL AUTO_INCREMENT,
  `n_documento` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombres` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellidos` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `telefono` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direccion` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `acudiente` tinyint(1) DEFAULT '0',
  `vive` tinyint(1) DEFAULT '0',
  `is_deleted` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_acudiente`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Familiares`
--

LOCK TABLES `Familiares` WRITE;
/*!40000 ALTER TABLE `Familiares` DISABLE KEYS */;
INSERT INTO `Familiares` VALUES (1,'1036668646','FABIO','MARQUEZ','3016414872','carrera 43a # 19-144 (notaría 15 de medellín)','fabiomarquez@gmail.com',1,1,0),(2,'1214740388','MARTHA','JIMENEZ MARQUEZ','3016414872','calle 3 # 78 - 19','davidrestrepovera@gmail.com',1,1,0);
/*!40000 ALTER TABLE `Familiares` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `FechasServicio`
--

DROP TABLE IF EXISTS `FechasServicio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `FechasServicio` (
  `id_fecha_servicio` int NOT NULL AUTO_INCREMENT,
  `id_servicio_contratado` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  PRIMARY KEY (`id_fecha_servicio`),
  KEY `id_servicio_contratado` (`id_servicio_contratado`),
  CONSTRAINT `FechasServicio_ibfk_1` FOREIGN KEY (`id_servicio_contratado`) REFERENCES `ServiciosPorContrato` (`id_servicio_contratado`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=888 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `FechasServicio`
--

LOCK TABLES `FechasServicio` WRITE;
/*!40000 ALTER TABLE `FechasServicio` DISABLE KEYS */;
INSERT INTO `FechasServicio` VALUES (812,101,'2025-07-07'),(813,101,'2025-07-14'),(814,101,'2025-07-21'),(815,101,'2025-07-28'),(816,101,'2025-07-29'),(817,101,'2025-07-22'),(818,101,'2025-07-15'),(819,101,'2025-07-08'),(820,101,'2025-07-30'),(821,101,'2025-07-23'),(822,101,'2025-07-16'),(823,101,'2025-07-09'),(824,101,'2025-07-31'),(825,101,'2025-07-24'),(826,101,'2025-07-17'),(827,101,'2025-07-10'),(828,101,'2025-07-11'),(829,101,'2025-07-18'),(830,101,'2025-07-25'),(831,101,'2025-08-01'),(832,102,'2025-07-07'),(833,102,'2025-07-14'),(834,102,'2025-07-21'),(835,102,'2025-07-28'),(836,102,'2025-07-29'),(837,102,'2025-07-22'),(838,102,'2025-07-15'),(839,102,'2025-07-08'),(840,102,'2025-07-09'),(841,102,'2025-07-16'),(842,102,'2025-07-23'),(843,102,'2025-07-30'),(844,102,'2025-07-31'),(845,102,'2025-07-24'),(846,102,'2025-07-17'),(847,102,'2025-07-10'),(848,102,'2025-07-11'),(849,102,'2025-07-18'),(850,102,'2025-07-25'),(851,102,'2025-08-01'),(852,103,'2025-07-31'),(853,103,'2025-07-30'),(854,103,'2025-07-29'),(855,103,'2025-07-28'),(856,105,'2025-07-07'),(857,105,'2025-07-08'),(858,105,'2025-07-09'),(859,105,'2025-07-10'),(860,106,'2025-07-07'),(861,106,'2025-07-08'),(862,106,'2025-07-09'),(863,106,'2025-07-10'),(864,107,'2025-07-07'),(865,107,'2025-07-08'),(866,107,'2025-07-09'),(867,107,'2025-07-10'),(868,108,'2025-07-07'),(869,108,'2025-07-08'),(870,108,'2025-07-09'),(871,108,'2025-07-10'),(872,109,'2025-07-07'),(873,109,'2025-07-08'),(874,109,'2025-07-09'),(875,109,'2025-07-10'),(876,110,'2025-07-07'),(877,110,'2025-07-08'),(878,110,'2025-07-09'),(879,110,'2025-07-10'),(880,111,'2025-07-07'),(881,111,'2025-07-08'),(882,111,'2025-07-09'),(883,111,'2025-07-10'),(884,112,'2025-07-07'),(885,112,'2025-07-08'),(886,112,'2025-07-09'),(887,112,'2025-07-10');
/*!40000 ALTER TABLE `FechasServicio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `HistoriaClinica`
--

DROP TABLE IF EXISTS `HistoriaClinica`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `HistoriaClinica` (
  `id_historiaclinica` int NOT NULL AUTO_INCREMENT,
  `Tiene_OtrasAlergias` tinyint(1) NOT NULL,
  `Tienedieta_especial` tinyint(1) NOT NULL,
  `alcoholismo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `alergico_medicamento` tinyint(1) NOT NULL,
  `altura` int NOT NULL,
  `apariencia_personal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `cafeina` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `cirugias` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `comunicacion_no_verbal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `comunicacion_verbal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `continencia` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `cuidado_personal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `dieta_especial` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `diagnosticos` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `discapacidades` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `emer_medica` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `eps` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado_de_animo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `fecha_ingreso` date NOT NULL,
  `frecuencia_cardiaca` decimal(10,0) NOT NULL,
  `historial_cirugias` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `id_usuario` int NOT NULL,
  `limitaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `maltratado` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `maltrato` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `medicamentos_alergia` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `motivo_ingreso` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `observ_dietaEspecial` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `observ_otrasalergias` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `observaciones_iniciales` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `otras_alergias` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `peso` decimal(10,0) NOT NULL,
  `presion_arterial` decimal(10,0) NOT NULL,
  `sustanciaspsico` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `tabaquismo` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `telefono_emermedica` varchar(17) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `temperatura_corporal` decimal(10,0) NOT NULL,
  `tipo_alimentacion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `tipo_de_movilidad` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `tipo_de_sueno` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `tipo_sangre` enum('A+','A-','B+','B-','AB+','AB-','O+','O-') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id_historiaclinica`),
  KEY `id_usuario` (`id_usuario`),
  CONSTRAINT `HistoriaClinica_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `Usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `HistoriaClinica`
--

LOCK TABLES `HistoriaClinica` WRITE;
/*!40000 ALTER TABLE `HistoriaClinica` DISABLE KEYS */;
INSERT INTO `HistoriaClinica` VALUES (1,1,1,'0',1,173,'buena','1','Cirugía de extracción de mama derecha:2023-01-05','pasiva','activa','0','independiente','3 COMIDAS AL DÍA,SIN HARINAS NI CARBOHIDRATOS',NULL,'Discapacidad lumbar','emi','SURA','ansioso','2025-05-05',15,'',1,'Dificultad para ahacharse y girar el cuello a la izquierda','0','0','IBUPROFENO,ACETAMINOPHEN','Aqui se agrega el motivo de ingreso','','','Aquí se agregan las observaciones del diagnóstico inicial','ALERGICO AL MANÍ',59,28,'0','0','6043214545',32,'normal','conAyuda','regular','O+'),(2,1,1,'1',1,173,'buena','0','OBSERVACIÓN 1:2025-05-01','pasiva','activa','0','conAyudaParcial','DIETA 1',NULL,'HOSTEOPORÓSIS','cruz-roja','SURA','ansioso','2025-05-05',31,'',2,'LIMITACIÓN 1','0','0','MEDICAMENTO 2','Terapia cognitiva, motivo por el que llega al centro de día','','','Aquí se agregan las observaciones del diagnóstico inicial','ALERGIAS 1',57,23,'0','1','6043214545',32,'normal','independiente','regular','O+');
/*!40000 ALTER TABLE `HistoriaClinica` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `IntervencionPorUsuario`
--

DROP TABLE IF EXISTS `IntervencionPorUsuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `IntervencionPorUsuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_historiaClinica` int DEFAULT NULL,
  `diagnostico` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `frecuencia` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `intervencion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `id_historiaClinica` (`id_historiaClinica`),
  CONSTRAINT `IntervencionPorUsuario_ibfk_1` FOREIGN KEY (`id_historiaClinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `IntervencionPorUsuario`
--

LOCK TABLES `IntervencionPorUsuario` WRITE;
/*!40000 ALTER TABLE `IntervencionPorUsuario` DISABLE KEYS */;
INSERT INTO `IntervencionPorUsuario` VALUES (1,2,'UN DIAGNÓSTICO','CADA CUANTO','PRUEBA');
/*!40000 ALTER TABLE `IntervencionPorUsuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MedicamentosPorUsuario`
--

DROP TABLE IF EXISTS `MedicamentosPorUsuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MedicamentosPorUsuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_historiaClinica` int DEFAULT NULL,
  `medicamento` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `periodicidad` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `observaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `id_historiaClinica` (`id_historiaClinica`),
  CONSTRAINT `MedicamentosPorUsuario_ibfk_1` FOREIGN KEY (`id_historiaClinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MedicamentosPorUsuario`
--

LOCK TABLES `MedicamentosPorUsuario` WRITE;
/*!40000 ALTER TABLE `MedicamentosPorUsuario` DISABLE KEYS */;
INSERT INTO `MedicamentosPorUsuario` VALUES (1,1,'ACETAMINOPHEN','CADA 12 HORAS',NULL),(2,2,'MEDICAMENTO 1','CADA CUANTO',NULL);
/*!40000 ALTER TABLE `MedicamentosPorUsuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `MetodoPago`
--

DROP TABLE IF EXISTS `MetodoPago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `MetodoPago` (
  `id_metodo_pago` int NOT NULL AUTO_INCREMENT,
  `nombre` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_metodo_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `MetodoPago`
--

LOCK TABLES `MetodoPago` WRITE;
/*!40000 ALTER TABLE `MetodoPago` DISABLE KEYS */;
INSERT INTO `MetodoPago` VALUES (1,'Efectivo'),(2,'Débito'),(3,'Crédito'),(4,'Cheque'),(5,'Otro');
/*!40000 ALTER TABLE `MetodoPago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `OrientacionEspacial`
--

DROP TABLE IF EXISTS `OrientacionEspacial`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `OrientacionEspacial` (
  `id_OrientacionEspacial` int NOT NULL AUTO_INCREMENT,
  `nom_OrientacionEspacial` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_OrientacionEspacial`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `OrientacionEspacial`
--

LOCK TABLES `OrientacionEspacial` WRITE;
/*!40000 ALTER TABLE `OrientacionEspacial` DISABLE KEYS */;
/*!40000 ALTER TABLE `OrientacionEspacial` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Pagos`
--

DROP TABLE IF EXISTS `Pagos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Pagos` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `id_factura` int DEFAULT NULL,
  `id_metodo_pago` int DEFAULT NULL,
  `id_tipo_pago` int DEFAULT NULL,
  `fecha_pago` date DEFAULT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_pago`),
  KEY `id_factura` (`id_factura`),
  KEY `id_metodo_pago` (`id_metodo_pago`),
  KEY `id_tipo_pago` (`id_tipo_pago`),
  CONSTRAINT `Pagos_ibfk_1` FOREIGN KEY (`id_factura`) REFERENCES `Facturas` (`id_factura`) ON DELETE CASCADE,
  CONSTRAINT `Pagos_ibfk_2` FOREIGN KEY (`id_metodo_pago`) REFERENCES `MetodoPago` (`id_metodo_pago`),
  CONSTRAINT `Pagos_ibfk_3` FOREIGN KEY (`id_tipo_pago`) REFERENCES `TipoPago` (`id_tipo_pago`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Pagos`
--

LOCK TABLES `Pagos` WRITE;
/*!40000 ALTER TABLE `Pagos` DISABLE KEYS */;
/*!40000 ALTER TABLE `Pagos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Profesionales`
--

DROP TABLE IF EXISTS `Profesionales`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Profesionales` (
  `id_profesional` int NOT NULL AUTO_INCREMENT,
  `nombres` varchar(35) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `apellidos` varchar(35) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `n_documento` varchar(25) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `t_profesional` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `fecha_ingreso` date DEFAULT NULL,
  `estado` enum('Activo','Inactivo') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `profesion` enum('Médico','Enfermero','Nutricionista','Psicólogo','Fisioterapeuta') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `especialidad` enum('Cardiología','Pediatría','Nutrición','Psicología Clínica','Fisioterapia') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cargo` enum('Jefe de Departamento','Especialista','Residente') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telefono` int DEFAULT NULL,
  `e_mail` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `direccion` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id_profesional`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Profesionales`
--

LOCK TABLES `Profesionales` WRITE;
/*!40000 ALTER TABLE `Profesionales` DISABLE KEYS */;
INSERT INTO `Profesionales` VALUES (1,'ANDREA','SALAZAR','1036654498','ABC-123456','1994-05-07','2025-05-05','Activo','Psicólogo','Psicología Clínica','Jefe de Departamento',312124547,'andreasalazar@correo.com','calle 3s # 35 - 19');
/*!40000 ALTER TABLE `Profesionales` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ReportesClinicos`
--

DROP TABLE IF EXISTS `ReportesClinicos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ReportesClinicos` (
  `id_reporteclinico` int NOT NULL AUTO_INCREMENT,
  `id_historiaclinica` int DEFAULT NULL,
  `id_profesional` int DEFAULT NULL,
  `Circunferencia_cadera` float DEFAULT NULL,
  `Frecuencia_cardiaca` int DEFAULT NULL,
  `IMC` decimal(5,2) DEFAULT NULL,
  `Obs_habitosalimenticios` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `Porc_grasacorporal` decimal(5,2) DEFAULT NULL,
  `Porc_masamuscular` decimal(5,2) DEFAULT NULL,
  `area_afectiva` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `area_comportamental` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `areacognitiva` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `areainterpersonal` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `areasomatica` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `circunferencia_cintura` float DEFAULT NULL,
  `consumo_aguadiaria` float DEFAULT NULL,
  `diagnostico` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `fecha_registro` date DEFAULT NULL,
  `frecuencia_actividadfisica` enum('Baja','Moderada','Alta') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `frecuencia_respiratoria` int DEFAULT NULL,
  `motivo_consulta` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `nivel_dolor` int DEFAULT NULL,
  `observaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `peso` int DEFAULT NULL,
  `presion_arterial` int DEFAULT NULL,
  `pruebas_examenes` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `recomendaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `remision` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `saturacionOxigeno` int DEFAULT NULL,
  `temperatura_corporal` float DEFAULT NULL,
  `tipo_reporte` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_reporteclinico`),
  KEY `id_historiaclinica` (`id_historiaclinica`),
  KEY `id_profesional` (`id_profesional`),
  CONSTRAINT `ReportesClinicos_ibfk_1` FOREIGN KEY (`id_historiaclinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE,
  CONSTRAINT `ReportesClinicos_ibfk_2` FOREIGN KEY (`id_profesional`) REFERENCES `Profesionales` (`id_profesional`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ReportesClinicos`
--

LOCK TABLES `ReportesClinicos` WRITE;
/*!40000 ALTER TABLE `ReportesClinicos` DISABLE KEYS */;
INSERT INTO `ReportesClinicos` VALUES (1,1,1,NULL,NULL,NULL,'Campo para agegar observaciones',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'UN DIAGNÓSTICO','2025-05-03',NULL,NULL,'Agregar motivo de consulta',NULL,'Campo para agregar observaciones internas',48,23,NULL,NULL,'especialista',132,32,'psicologia'),(2,2,1,NULL,NULL,NULL,'Observaciones',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'UN DIAGNÓSTICO','2025-05-05',NULL,NULL,'Agregar motivo de consulta',NULL,'Aquí se agregan observaciones internas',45,23,NULL,NULL,'especialista',132,32,'psicologia'),(3,1,1,NULL,NULL,NULL,'Se recomienda acompañamiento psicológico.\nAlimentación baja en gluten y grasas',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'Se considera que el adulto padece maltrato','2025-04-30',NULL,NULL,'Adulto mayor con depresión y ansiedad',NULL,'Se comporta de froma agresiva y poco amable con personal profesional, pero secomporta lo contrario con sus compañeros.',58,41,NULL,'Recomendaciones aquí','no_aplica',10,55,'psicologia'),(4,1,1,NULL,NULL,NULL,'OBSERVACIÓN (tratamientos y recomendaciones)',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'DIAGNÓSTICO','2025-05-10',NULL,NULL,'MOTIVO DE LA CONSULTA',NULL,'OBSERVACIONES INTERNAS',1,2,NULL,'Recomendaciones aquí','especialista',5,4,'enfermeria');
/*!40000 ALTER TABLE `ReportesClinicos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Servicios`
--

DROP TABLE IF EXISTS `Servicios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Servicios` (
  `id_servicio` int NOT NULL AUTO_INCREMENT,
  `nombre` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Servicios`
--

LOCK TABLES `Servicios` WRITE;
/*!40000 ALTER TABLE `Servicios` DISABLE KEYS */;
INSERT INTO `Servicios` VALUES (1,'Cuidado',NULL),(2,'Transporte',NULL),(3,'Servicio de Día',NULL);
/*!40000 ALTER TABLE `Servicios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ServiciosPorContrato`
--

DROP TABLE IF EXISTS `ServiciosPorContrato`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ServiciosPorContrato` (
  `id_servicio_contratado` int NOT NULL AUTO_INCREMENT,
  `id_contrato` int DEFAULT NULL,
  `id_servicio` int DEFAULT NULL,
  `fecha` date DEFAULT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `precio_por_dia` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_servicio_contratado`),
  KEY `id_contrato` (`id_contrato`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `ServiciosPorContrato_ibfk_1` FOREIGN KEY (`id_contrato`) REFERENCES `Contratos` (`id_contrato`) ON DELETE CASCADE,
  CONSTRAINT `ServiciosPorContrato_ibfk_2` FOREIGN KEY (`id_servicio`) REFERENCES `Servicios` (`id_servicio`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ServiciosPorContrato`
--

LOCK TABLES `ServiciosPorContrato` WRITE;
/*!40000 ALTER TABLE `ServiciosPorContrato` DISABLE KEYS */;
INSERT INTO `ServiciosPorContrato` VALUES (101,1,1,'2025-07-06','',0.00),(102,1,2,'2025-07-06','',0.00),(103,2,1,'2025-07-07','',0.00),(104,2,3,'2025-07-07','',0.00),(105,3,1,'2025-07-07','',0.00),(106,3,2,'2025-07-07','',0.00),(107,4,1,'2025-07-07','',0.00),(108,4,2,'2025-07-07','',0.00),(109,5,1,'2025-07-07','',0.00),(110,6,1,'2025-07-07','',0.00),(111,7,1,'2025-07-07','',0.00),(112,7,2,'2025-07-07','',0.00);
/*!40000 ALTER TABLE `ServiciosPorContrato` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TarifasServicioPorAnio`
--

DROP TABLE IF EXISTS `TarifasServicioPorAnio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TarifasServicioPorAnio` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_servicio` int DEFAULT NULL,
  `anio` year NOT NULL,
  `precio_por_dia` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_servicio` (`id_servicio`),
  CONSTRAINT `TarifasServicioPorAnio_ibfk_1` FOREIGN KEY (`id_servicio`) REFERENCES `Servicios` (`id_servicio`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TarifasServicioPorAnio`
--

LOCK TABLES `TarifasServicioPorAnio` WRITE;
/*!40000 ALTER TABLE `TarifasServicioPorAnio` DISABLE KEYS */;
INSERT INTO `TarifasServicioPorAnio` VALUES (1,1,2025,150000.00),(2,2,2025,50000.00),(3,3,2025,25000.00);
/*!40000 ALTER TABLE `TarifasServicioPorAnio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TipoActividad`
--

DROP TABLE IF EXISTS `TipoActividad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TipoActividad` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TipoActividad`
--

LOCK TABLES `TipoActividad` WRITE;
/*!40000 ALTER TABLE `TipoActividad` DISABLE KEYS */;
INSERT INTO `TipoActividad` VALUES (1,'GRUPAL');
/*!40000 ALTER TABLE `TipoActividad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TipoDiscaPorUsuarios`
--

DROP TABLE IF EXISTS `TipoDiscaPorUsuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TipoDiscaPorUsuarios` (
  `id_tipodiscapacidad` int NOT NULL,
  `id_historiaClinica` int NOT NULL,
  `observación` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_tipodiscapacidad`,`id_historiaClinica`),
  KEY `id_historiaClinica` (`id_historiaClinica`),
  CONSTRAINT `TipoDiscaPorUsuarios_ibfk_1` FOREIGN KEY (`id_tipodiscapacidad`) REFERENCES `TipoDiscapacidad` (`id_tipodiscapacidad`),
  CONSTRAINT `TipoDiscaPorUsuarios_ibfk_2` FOREIGN KEY (`id_historiaClinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TipoDiscaPorUsuarios`
--

LOCK TABLES `TipoDiscaPorUsuarios` WRITE;
/*!40000 ALTER TABLE `TipoDiscaPorUsuarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `TipoDiscaPorUsuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TipoLimitPorUsuarios`
--

DROP TABLE IF EXISTS `TipoLimitPorUsuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TipoLimitPorUsuarios` (
  `id_tipolimitacion` int NOT NULL,
  `id_historiaClinica` int NOT NULL,
  `observación` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_tipolimitacion`,`id_historiaClinica`),
  KEY `id_historiaClinica` (`id_historiaClinica`),
  CONSTRAINT `TipoLimitPorUsuarios_ibfk_1` FOREIGN KEY (`id_tipolimitacion`) REFERENCES `TipoLimitacion` (`id_tipolimitacion`),
  CONSTRAINT `TipoLimitPorUsuarios_ibfk_2` FOREIGN KEY (`id_historiaClinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TipoLimitPorUsuarios`
--

LOCK TABLES `TipoLimitPorUsuarios` WRITE;
/*!40000 ALTER TABLE `TipoLimitPorUsuarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `TipoLimitPorUsuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TipoPago`
--

DROP TABLE IF EXISTS `TipoPago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TipoPago` (
  `id_tipo_pago` int NOT NULL AUTO_INCREMENT,
  `nombre` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_tipo_pago`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TipoPago`
--

LOCK TABLES `TipoPago` WRITE;
/*!40000 ALTER TABLE `TipoPago` DISABLE KEYS */;
/*!40000 ALTER TABLE `TipoPago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `TipoReporteClinico`
--

DROP TABLE IF EXISTS `TipoReporteClinico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `TipoReporteClinico` (
  `id_TipoReporte` int NOT NULL AUTO_INCREMENT,
  `nom_TipoReporte` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_TipoReporte`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `TipoReporteClinico`
--

LOCK TABLES `TipoReporteClinico` WRITE;
/*!40000 ALTER TABLE `TipoReporteClinico` DISABLE KEYS */;
/*!40000 ALTER TABLE `TipoReporteClinico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `Usuarios`
--

DROP TABLE IF EXISTS `Usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `Usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `n_documento` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombres` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellidos` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `genero` enum('Masculino','Femenino','Neutro') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `direccion` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telefono` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ocupacion_quedesempeño` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `estado_civil` enum('Soltero','Casado','Viudo','Unión Libre','Divorciado') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` enum('ACTIVO','INACTIVO') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'ACTIVO',
  `tipo_usuario` enum('Nuevo','Recurrente') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT 'Nuevo',
  `profesion` varchar(70) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  `lugar_nacimiento` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `regimen_seguridad_social` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `grado_escolaridad` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tipo_afiliacion` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `escribe` tinyint(1) DEFAULT '0',
  `lee` tinyint(1) DEFAULT '0',
  `lugar_procedencia` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `ha_estado_en_otro_centro` tinyint(1) DEFAULT '0',
  `origen_otrocentro` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `proteccion_exequial` tinyint(1) DEFAULT '0',
  `nucleo_familiar` enum('Nuclear','Extensa','Monoparental','Reconstituida') CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `url_imagen` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `is_deleted` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `Usuarios`
--

LOCK TABLES `Usuarios` WRITE;
/*!40000 ALTER TABLE `Usuarios` DISABLE KEYS */;
INSERT INTO `Usuarios` VALUES (1,'1036668393','DAVID','RESTREPO VERA','1972-05-12','Masculino','calle 3 # 78 - 19','3016414872','davidrestrepovera@gmail.com',NULL,'Divorciado','ACTIVO','Nuevo',NULL,'2025-05-05 19:14:09',NULL,NULL,NULL,NULL,0,0,NULL,0,NULL,0,'Nuclear',NULL,0),(2,'1214740388','FABIO','MARQUEZ','1989-05-11','Masculino','calle 3 # 78 - 19','3016414872','davidrestrepovera234@gmail.com',NULL,'Casado','ACTIVO','Nuevo',NULL,'2025-05-05 22:13:20',NULL,NULL,NULL,NULL,0,0,NULL,0,NULL,0,'Nuclear',NULL,0),(3,'147258369','JUAN CAMILO','MADRID ORTEGA','1985-05-10','Masculino','calle 3 # 78 - 19','3016414889','juancamilo@gmail.com',NULL,'Soltero','ACTIVO','Nuevo',NULL,'2025-05-11 00:20:03',NULL,NULL,NULL,NULL,0,0,NULL,0,NULL,0,'Nuclear',NULL,0);
/*!40000 ALTER TABLE `Usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `VacunasPorUsuario`
--

DROP TABLE IF EXISTS `VacunasPorUsuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `VacunasPorUsuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_historiaClinica` int DEFAULT NULL,
  `efectos_secundarios` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `fecha_administracion` date DEFAULT NULL,
  `fecha_proxima` date DEFAULT NULL,
  `vacuna` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `id_historiaClinica` (`id_historiaClinica`),
  CONSTRAINT `VacunasPorUsuario_ibfk_1` FOREIGN KEY (`id_historiaClinica`) REFERENCES `HistoriaClinica` (`id_historiaclinica`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `VacunasPorUsuario`
--

LOCK TABLES `VacunasPorUsuario` WRITE;
/*!40000 ALTER TABLE `VacunasPorUsuario` DISABLE KEYS */;
INSERT INTO `VacunasPorUsuario` VALUES (1,1,'VISIÓN NUBLADA','2025-04-30','2025-05-31','TÉTANO'),(2,1,'2 DOSIS DE VACUNA COVID 19 PHISER','2022-02-01','2023-05-02','COVID');
/*!40000 ALTER TABLE `VacunasPorUsuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `configuracion_rutas`
--

DROP TABLE IF EXISTS `configuracion_rutas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `configuracion_rutas` (
  `id_configuracion` int NOT NULL AUTO_INCREMENT,
  `id_profesional` int NOT NULL,
  `nombre_ruta` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `descripcion` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `activa` tinyint(1) DEFAULT '1',
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_configuracion`),
  KEY `idx_profesional` (`id_profesional`),
  KEY `idx_activa` (`activa`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `configuracion_rutas`
--

LOCK TABLES `configuracion_rutas` WRITE;
/*!40000 ALTER TABLE `configuracion_rutas` DISABLE KEYS */;
/*!40000 ALTER TABLE `configuracion_rutas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cronograma_asistencia`
--

DROP TABLE IF EXISTS `cronograma_asistencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cronograma_asistencia` (
  `id_cronograma` int NOT NULL AUTO_INCREMENT,
  `id_profesional` int NOT NULL,
  `fecha` date NOT NULL,
  `comentario` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_cronograma`),
  KEY `id_profesional` (`id_profesional`),
  CONSTRAINT `cronograma_asistencia_ibfk_1` FOREIGN KEY (`id_profesional`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cronograma_asistencia`
--

LOCK TABLES `cronograma_asistencia` WRITE;
/*!40000 ALTER TABLE `cronograma_asistencia` DISABLE KEYS */;
INSERT INTO `cronograma_asistencia` VALUES (1,1,'2025-07-07','Generado automáticamente desde contrato 1'),(2,1,'2025-07-31','Generado automáticamente desde contrato 1'),(3,1,'2025-07-23','Generado automáticamente desde contrato 1'),(4,1,'2025-07-16','Generado automáticamente desde contrato 1'),(5,1,'2025-07-08','Generado automáticamente desde contrato 1'),(6,1,'2025-07-09','Generado automáticamente desde contrato 1'),(7,1,'2025-07-11','Generado automáticamente desde contrato 1'),(8,1,'2025-07-18','Generado automáticamente desde contrato 1'),(9,1,'2025-07-24','Generado automáticamente desde contrato 1'),(10,1,'2025-07-22','Generado automáticamente desde contrato 1'),(11,1,'2025-07-10','Generado automáticamente desde contrato 1'),(12,1,'2025-08-01','Generado automáticamente desde contrato 1'),(13,1,'2025-07-15','Generado automáticamente desde contrato 1'),(14,1,'2025-07-30','Generado automáticamente desde contrato 1'),(15,1,'2025-07-25','Generado automáticamente desde contrato 1'),(16,1,'2025-07-29','Generado automáticamente desde contrato 1'),(17,1,'2025-07-28','Generado automáticamente desde contrato 1'),(18,1,'2025-07-14','Generado automáticamente desde contrato 1'),(19,1,'2025-07-21','Generado automáticamente desde contrato 1'),(20,1,'2025-07-17','Generado automáticamente desde contrato 1');
/*!40000 ALTER TABLE `cronograma_asistencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cronograma_asistencia_pacientes`
--

DROP TABLE IF EXISTS `cronograma_asistencia_pacientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cronograma_asistencia_pacientes` (
  `id_cronograma_paciente` int NOT NULL AUTO_INCREMENT,
  `id_cronograma` int NOT NULL,
  `id_usuario` int NOT NULL,
  `id_contrato` int NOT NULL,
  `estado_asistencia` enum('PENDIENTE','ASISTIO','NO_ASISTIO','CANCELADO','REAGENDADO') COLLATE utf8mb4_unicode_ci DEFAULT 'PENDIENTE',
  `requiere_transporte` tinyint(1) DEFAULT '0',
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_cronograma_paciente`),
  KEY `id_cronograma` (`id_cronograma`),
  KEY `id_usuario` (`id_usuario`),
  KEY `id_contrato` (`id_contrato`),
  CONSTRAINT `cronograma_asistencia_pacientes_ibfk_1` FOREIGN KEY (`id_cronograma`) REFERENCES `cronograma_asistencia` (`id_cronograma`) ON DELETE CASCADE,
  CONSTRAINT `cronograma_asistencia_pacientes_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `Usuarios` (`id_usuario`),
  CONSTRAINT `cronograma_asistencia_pacientes_ibfk_3` FOREIGN KEY (`id_contrato`) REFERENCES `Contratos` (`id_contrato`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cronograma_asistencia_pacientes`
--

LOCK TABLES `cronograma_asistencia_pacientes` WRITE;
/*!40000 ALTER TABLE `cronograma_asistencia_pacientes` DISABLE KEYS */;
INSERT INTO `cronograma_asistencia_pacientes` VALUES (1,1,1,1,'ASISTIO',1,NULL),(2,2,1,1,'PENDIENTE',1,NULL),(3,3,1,1,'PENDIENTE',1,NULL),(4,4,1,1,'PENDIENTE',1,NULL),(5,5,1,1,'ASISTIO',1,NULL),(6,6,1,1,'PENDIENTE',1,NULL),(7,7,1,1,'PENDIENTE',1,NULL),(8,8,1,1,'PENDIENTE',1,NULL),(9,9,1,1,'PENDIENTE',1,NULL),(10,10,1,1,'PENDIENTE',1,NULL),(11,11,1,1,'PENDIENTE',1,NULL),(12,12,1,1,'PENDIENTE',1,NULL),(13,13,1,1,'PENDIENTE',1,NULL),(14,14,1,1,'PENDIENTE',1,NULL),(15,15,1,1,'PENDIENTE',1,NULL),(16,16,1,1,'PENDIENTE',1,NULL),(17,17,1,1,'PENDIENTE',1,NULL),(18,18,1,1,'PENDIENTE',1,NULL),(19,19,1,1,'PENDIENTE',1,NULL),(20,20,1,1,'PENDIENTE',1,NULL),(21,5,2,7,'REAGENDADO',1,'No asiste porque no'),(22,6,2,7,'PENDIENTE',1,NULL),(23,1,2,7,'NO_ASISTIO',1,''),(24,11,2,7,'PENDIENTE',1,NULL),(25,2,2,7,'PENDIENTE',0,'');
/*!40000 ALTER TABLE `cronograma_asistencia_pacientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cronograma_transporte`
--

DROP TABLE IF EXISTS `cronograma_transporte`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cronograma_transporte` (
  `id_transporte` int NOT NULL AUTO_INCREMENT,
  `id_cronograma_paciente` int NOT NULL,
  `direccion_recogida` text COLLATE utf8mb4_unicode_ci,
  `direccion_entrega` text COLLATE utf8mb4_unicode_ci,
  `hora_recogida` time DEFAULT NULL,
  `hora_entrega` time DEFAULT NULL,
  `estado` enum('PENDIENTE','REALIZADO','CANCELADO') COLLATE utf8mb4_unicode_ci DEFAULT 'PENDIENTE',
  `observaciones` text COLLATE utf8mb4_unicode_ci,
  `fecha_creacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `fecha_actualizacion` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_transporte`),
  KEY `idx_estado` (`estado`),
  KEY `idx_fecha_creacion` (`fecha_creacion`),
  KEY `idx_cronograma_paciente` (`id_cronograma_paciente`),
  KEY `idx_hora_recogida` (`hora_recogida`),
  CONSTRAINT `cronograma_transporte_ibfk_1` FOREIGN KEY (`id_cronograma_paciente`) REFERENCES `cronograma_asistencia_pacientes` (`id_cronograma_paciente`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cronograma_transporte`
--

LOCK TABLES `cronograma_transporte` WRITE;
/*!40000 ALTER TABLE `cronograma_transporte` DISABLE KEYS */;
INSERT INTO `cronograma_transporte` VALUES (1,1,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(2,2,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(3,3,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(4,4,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(5,5,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(6,6,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(7,7,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(8,8,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(9,9,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(10,10,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(11,11,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(12,12,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(13,13,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(14,14,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(15,15,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(16,16,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(17,17,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(18,18,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(19,19,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(20,20,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:12:59',NULL),(21,21,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:25:34',NULL),(22,22,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:25:34',NULL),(23,23,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:25:34',NULL),(24,24,'Por definir','Por definir','08:00:00','17:00:00','PENDIENTE','Generado automáticamente desde contrato','2025-07-06 22:25:34',NULL);
/*!40000 ALTER TABLE `cronograma_transporte` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `familiares_y_acudientes_por_usuario`
--

DROP TABLE IF EXISTS `familiares_y_acudientes_por_usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `familiares_y_acudientes_por_usuario` (
  `id_acudiente` int NOT NULL,
  `id_usuario` int NOT NULL,
  `parentesco` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id_acudiente`,`id_usuario`),
  KEY `fk_usuario` (`id_usuario`),
  CONSTRAINT `fk_acudiente` FOREIGN KEY (`id_acudiente`) REFERENCES `Familiares` (`id_acudiente`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `Usuarios` (`id_usuario`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `familiares_y_acudientes_por_usuario`
--

LOCK TABLES `familiares_y_acudientes_por_usuario` WRITE;
/*!40000 ALTER TABLE `familiares_y_acudientes_por_usuario` DISABLE KEYS */;
INSERT INTO `familiares_y_acudientes_por_usuario` VALUES (1,1,'Hermano'),(2,2,'Hermana');
/*!40000 ALTER TABLE `familiares_y_acudientes_por_usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `historial_transporte`
--

DROP TABLE IF EXISTS `historial_transporte`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `historial_transporte` (
  `id_historial` int NOT NULL AUTO_INCREMENT,
  `id_transporte` int NOT NULL,
  `estado_anterior` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado_nuevo` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `observaciones` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `fecha_cambio` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `id_usuario_cambio` int DEFAULT NULL,
  PRIMARY KEY (`id_historial`),
  KEY `idx_transporte` (`id_transporte`),
  KEY `idx_fecha_cambio` (`fecha_cambio`),
  CONSTRAINT `historial_transporte_ibfk_1` FOREIGN KEY (`id_transporte`) REFERENCES `cronograma_transporte` (`id_transporte`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `historial_transporte`
--

LOCK TABLES `historial_transporte` WRITE;
/*!40000 ALTER TABLE `historial_transporte` DISABLE KEYS */;
/*!40000 ALTER TABLE `historial_transporte` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `first_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_deleted` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'davidrestrepovera@gmail.com','DAVID','RESTREPO VERA','$2b$12$yKYNlX3iZ9Zu9BFlGrWvNOv9C4wY2AcKlazrf71fk/2MxqCracG.u',0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-06 18:24:30
